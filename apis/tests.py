from datetime import timedelta
from http.client import UNAUTHORIZED

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.models import NewElection, NewCandidate, NewArea, NewParty, VoteResultParty, VoteResultCandidate, VoteCheck
from django.utils import timezone

import json


class VoteApiTest(APITestCase):
    def setUp(self) -> None:
        """Create election for testing."""
        self.election = NewElection.objects.create(name="Test election",
                                                   start_date=timezone.now(),
                                                   end_date=timezone.now() + timedelta(days=1))

        self.users = [
            # Candidates
            User.objects.create_user(username="p1", email="p1@email.com", password="BadPassword"),
            User.objects.create_user(username="p2", email="p2@email.com", password="BadPassword"),
            User.objects.create_user(username="p3", email="p3@email.com", password="BadPassword"),
            # Not candidates
            User.objects.create_user(username="p4", email="p4@email.com", password="BadPassword"),
        ]
        self.areas = [
            NewArea.objects.create(name="A1"),
            NewArea.objects.create(name="A2"),
        ]
        self.users[0].newprofile.area = self.areas[0]
        self.users[0].newprofile.save()
        self.users[1].newprofile.area = self.areas[0]
        self.users[1].newprofile.save()
        self.users[2].newprofile.area = self.areas[1]
        self.users[2].newprofile.save()
        self.users[3].newprofile.area = self.areas[1]
        self.users[3].newprofile.save()
        self.candidates = [
            NewCandidate.objects.create(user=self.users[0], area=self.areas[0]),
            NewCandidate.objects.create(user=self.users[1], area=self.areas[0]),
            NewCandidate.objects.create(user=self.users[2], area=self.areas[1]),
        ]
        self.parties = [
            NewParty.objects.create(name="PT1"),
            NewParty.objects.create(name="PT2"),
        ]
        self.parties[0].newcandidate_set.add(self.candidates[0])
        self.parties[0].newcandidate_set.add(self.candidates[1])
        self.parties[0].save()
        self.parties[1].newcandidate_set.add(self.candidates[2])
        self.parties[1].save()
        self.test_url = reverse('api_election_vote', args=[self.election.id])

    def test_vote_work(self):
        """
        Test normal case that should work.
        """
        self.client.force_login(self.users[0])
        response = self.client.post(self.test_url)
        self.assertEqual(response.status_code, 201)
        party_result = VoteResultParty.objects.get(election=self.election, party=self.parties[0])
        self.assertEqual(party_result.vote, 1)
        candidate_result = VoteResultCandidate.objects.get(election=self.election, candidate=self.candidates[0])
        self.assertEqual(candidate_result.vote, 1)
        self.assertTrue(VoteCheck.objects.filter(user=self.users[0], election=self.election).exists())

    def test_vote_unauthenticated(self):
        """
        Test voting without authentication
        """
        response = self.client.post(self.test_url)
        self.assertEqual(response.status_code, UNAUTHORIZED)

    def test_vote_multiple_time(self):
        """
        Voting multiple times is not allowed.
        """
        self.client.force_login(self.users[0])
        VoteCheck.objects.create(user=self.users[0], election=self.election)
        response = self.client.post(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_vote_invalid_party(self):
        """Voting invalid party should not be possible"""
        self.client.force_login(self.users[1])
        response = self.client.post(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(VoteCheck.objects.filter(user=self.users[1], election=self.election).exists())

    def test_vote_invalid_candidate(self):
        """Voting invalid candidate should not be possible."""
        self.client.force_login(self.users[1])
        response = self.client.post(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(VoteCheck.objects.filter(user=self.users[1], election=self.election).exists())

    def test_vote_wrong_time(self):
        """Both upcoming and ended elections cannot be voted."""
        self.client.force_login(self.users[0])

        # Ended
        self.election.start_date -= timedelta(days=9)
        self.election.end_date -= timedelta(days=2)
        self.election.save()

        response = self.client.post(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg="Ended election should not be voted")
        self.assertFalse(VoteCheck.objects.filter(user=self.users[0], election=self.election).exists())

        # Upcoming
        self.election.end_date += timedelta(days=21)
        self.election.start_date += timedelta(days=10)
        self.election.save()
        response = self.client.post(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg="Upcoming election should not be voted")
        self.assertFalse(VoteCheck.objects.filter(user=self.users[0], election=self.election).exists())

    def test_vote_outside_area(self):
        """Voting candidate is only allowed in the same area."""
        self.client.force_login(self.users[3])
        response = self.client.post(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg="Cannot vote outside area")
        self.assertFalse(VoteCheck.objects.filter(user=self.users[3], election=self.election).exists())

    def test_vote_without_area(self):
        """If user does not have area, there should be a warning."""
        self.client.force_login(self.users[0])
        self.areas[0].newprofile_set.remove(self.users[0].newprofile)
        self.areas[0].save()
        response = self.client.post(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg="Must handle no area case")
        self.assertFalse(VoteCheck.objects.filter(user=self.users[0], election=self.election).exists())


class CandidateApiTest(APITestCase):
    def setUp(self):
        """Pre-test setup."""
        staff = User.objects.create_user(username="staff", email="staff@email.com", password="AmongUs")
        staff.is_staff = True
        staff.save()

        self.users = [
            # Staff
            staff,

            # Candidates
            User.objects.create_user(username="U1", email="pp1@email.com", password="AmongUs"),
            User.objects.create_user(username="U2", email="pp2@email.com", password="AmongUs"),
            User.objects.create_user(username="U3", email="pp3@email.com", password="AmongUs")
        ]

        self.areas = [
            NewArea.objects.create(name="A1"),
            NewArea.objects.create(name="A2"),
            NewArea.objects.create(name="A3")
        ]

        self.candidates = [
            NewCandidate.objects.create(user=self.users[1], area=self.areas[0]),
            NewCandidate.objects.create(user=self.users[2], area=self.areas[1]),
            NewCandidate.objects.create(user=self.users[3], area=self.areas[2])
        ]

        self.url = reverse('api_candidate_list')

    def test_get_has_candidates(self):
        """All available candidates should be returned."""

        response = self.client.get(self.url, format="json")
        response_content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_content["result"]), 3)

    def test_post_valid(self):
        """Happy path test on adding a candidate. It should pass no matter what."""
        test_user_id = User.objects.create_user(username="U4", email="pp4@email.com", password="AmongUs").id
        test_area_id = self.areas[2].id
        description = "Bla Bla Bla"

        self.client.force_login(self.users[0])
        response = self.client.post(self.url)
        response_content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_content["result"]["user"]["id"], test_user_id)
        self.assertEqual(response_content["result"]["description"], description)
        self.assertEqual(response_content["result"]["area"]["id"], test_area_id)
        self.assertTrue(NewCandidate.objects.filter(id=response_content["result"]["id"]).exists())

    def test_post_unauthorized_guest(self):
        """Guests should not be able to create a new candidate."""
        test_user_id = User.objects.create_user(username="U5", email="pp5@email.com", password="AmongUs").id
        test_area_id = self.areas[1].id
        description = "Bla Bla Bla Bleh"

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_unauthorized_user(self):
        """Users who are not admins should not be able to create a new candidate."""
        test_user_id = User.objects.create_user(username="U5", email="pp5@email.com", password="AmongUs").id
        test_area_id = self.areas[1].id
        description = "Bla Bla Bla Bleh"

        self.client.force_login(self.users[1])
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_no_user(self):
        """Creating a candidate should not be possible when provided user id does not exist."""
        test_user_id = -1
        test_area_id = self.areas[2].id
        description = "Bla Bla Bla"

        self.client.force_login(self.users[0])
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_no_area(self):
        """Creating a candidate should not be possible when provided area id does not exist."""
        test_user_id = User.objects.create_user(username="U6", email="pp6@email.com", password="AmongUs").id
        test_area_id = -1
        description = "Bla Bla Bla Bleh"

        self.client.force_login(self.users[0])
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_already_candidate(self):
        """Creating a candidate should not be possible when provided user is already a candidate."""
        test_user = User.objects.create_user(username="U7", email="pp7@email.com", password="AmongUs")
        test_area = self.areas[0]
        description = "Bla Bla Bla Bleh"
        NewCandidate.objects.create(user=test_user, area=test_area)

        self.client.force_login(self.users[0])
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_malformed(self):
        """Malformed request body should trigger an error."""
        test_user_id = User.objects.create_user(username="U8", email="pp8@email.com", password="AmongUs").id
        test_area_id = self.areas[2].id
        description = "Bla Bla Bla"

        self.client.force_login(self.users[0])
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_valid(self):
        """Collection of valid push requests. Should pass no matter what."""
        temp_user = User.objects.create_user(username="U9", email="pp9@email.com", password="AmongUs")
        test_candidate_id = NewCandidate.objects.create(user=temp_user, area=self.areas[0]).id
        test_user_id = User.objects.create_user(username="U10", email="pp10@email.com", password="AmongUs").id
        test_area_id = self.areas[0].id
        description = "So the FCC won't let me be so let me see..."

        self.client.force_login(self.users[0])
        response = self.client.put(self.url, {
            "candidate_id": self.candidates[0].id,
            "description": description,
        })
        response_content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_content["result"]["description"], description)

        response = self.client.put(self.url, {
            "candidate_id": self.candidates[0].id,
            "area_id": test_area_id,
        })
        response_content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_content["result"]["area"]["id"], test_area_id)

        response = self.client.put(self.url, {
            "candidate_id": self.candidates[0].id,
            "user_id": test_user_id
        })
        response_content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_content["result"]["user"]["id"], test_user_id)

        # Add users[1] back in. This means that it doesn't trigger "already a candidate" error.
        response = self.client.put(self.url, {
            "candidate_id": test_candidate_id,
            "user_id": self.users[1].id
        })
        response_content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_content["result"]["id"], test_candidate_id)

    def test_put_no_candidate(self):
        """If the provided candidate does not exist an error should be returned."""
        self.client.force_login(self.users[0])
        response = self.client.put(self.url, {
            "candidate_id": -1,
            "description": "hi",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_no_user(self):
        """If the provided user does not exist an error should be returned."""
        self.client.force_login(self.users[0])
        response = self.client.put(self.url, {
            "candidate_id": self.candidates[0].id,
            "user_id": -1,
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_no_area(self):
        """If he provided area does not exist an error should be returned."""
        self.client.force_login(self.users[0])
        response = self.client.put(self.url, {
            "candidate_id": self.candidates[0].id,
            "area_id": -1
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_user_already_candidate(self):
        """If the provided user is already a candidate they cannot be designated as another candidate."""
        temp_user = User.objects.create_user(username="U11", email="pp11@email.com", password="AmongUs")
        test_candidate_id = NewCandidate.objects.create(user=temp_user, area=self.areas[0]).id

        self.client.force_login(self.users[0])
        response = self.client.put(self.url, {
            "candidate_id": test_candidate_id,
            "user_id": self.users[2].id
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_unauthorized_guest(self):
        """Guests should not be able to modify candidate."""
        response = self.client.put(self.url, {
            "candidate_id": self.candidates[0].id,
            "description": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_unauthorized_user(self):
        """Users who are not staffs should not be able to modify candidate."""
        self.client.force_login(self.users[1])
        response = self.client.put(self.url, {
            "candidate_id": self.candidates[0].id,
            "description": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_malformed(self):
        """Malformed PUT request should trigger an error."""
        self.client.force_login(self.users[0])
        response = self.client.put(self.url, {
            "candidte_id": self.candidates[0].id,
            "user": self.users[1].id,
            "detion": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            "ara_id": self.areas[0].id
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_param_exist(self):
        """Get the detail of an existing candidate. Should pass."""
        self.client.force_login(self.users[0])
        response = self.client.get(reverse('api_candidate_detail', args=[self.candidates[0].id]))
        response_content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_content["candidate"]["id"], self.candidates[0].id)

    def test_get_param_nonexistent(self):
        """If the provided candidate doesn't exist then return an error."""
        self.client.force_login(self.users[0])
        response = self.client.get(reverse('api_candidate_detail', args=[123456790]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
class ElectionApiTest(APITestCase):
    def setUp(self) -> None:
        """Create election for testing."""
        self.election1 = NewElection.objects.create(name="Test election1",
                                                   start_date=timezone.now(),
                                                   end_date=timezone.now() + timedelta(days=1))

        self.election2 = NewElection.objects.create(name="Test election2",
                                                   start_date=timezone.now() + timedelta(days=2),
                                                   end_date=timezone.now() + timedelta(days=3))

        self.election3 = NewElection.objects.create(name="Test election3",
                                               start_date=timezone.now() + timedelta(days=4),
                                               end_date=timezone.now() + timedelta(days=5))

        self.users = [
            # Candidates
            User.objects.create_user(username="p1", email="p1@email.com", password="BadPassword"),
            User.objects.create_user(username="p2", email="p2@email.com", password="BadPassword"),
            User.objects.create_user(username="p3", email="p3@email.com", password="BadPassword"),
            # Not candidates
            User.objects.create_user(username="p4", email="p4@email.com", password="BadPassword"),
            # Superuser
            User.objects.create_superuser(username="sp1", email="sp1@email.com", password="BadPassword")
        ]
        self.areas = [
            NewArea.objects.create(name="A1"),
            NewArea.objects.create(name="A2"),
        ]
        self.users[0].newprofile.area = self.areas[0]
        self.users[0].newprofile.save()
        self.users[1].newprofile.area = self.areas[0]
        self.users[1].newprofile.save()
        self.users[2].newprofile.area = self.areas[1]
        self.users[2].newprofile.save()
        self.users[3].newprofile.area = self.areas[1]
        self.users[3].newprofile.save()
        self.candidates = [
            NewCandidate.objects.create(user=self.users[0], area=self.areas[0]),
            NewCandidate.objects.create(user=self.users[1], area=self.areas[0]),
            NewCandidate.objects.create(user=self.users[2], area=self.areas[1]),
        ]
        self.parties = [
            NewParty.objects.create(name="PT1"),
            NewParty.objects.create(name="PT2"),
        ]
        self.parties[0].newcandidate_set.add(self.candidates[0])
        self.parties[0].newcandidate_set.add(self.candidates[1])
        self.parties[0].save()
        self.parties[1].newcandidate_set.add(self.candidates[2])
        self.parties[1].save()
        # self.test_url = reverse('api_election_list')

    def test_get_list_election(self):
        """Test normal case of get all election list."""
        self.test_url = reverse('api_election_list')
        response = self.client.get(self.test_url)
        response_content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_content), 2)
        self.assertEqual(response_content["result"][0]["id"], 1)
        self.assertEqual(response_content["result"][0]["name"], 'Test election1')
        self.assertNotEqual(response_content["result"][0]["start_date"], None)
        self.assertNotEqual(response_content["result"][0]["end_date"], None)

    def test_start_election_not_login(self):
        """If user not login, they cannot start election."""
        self.test_url = reverse('api_election_list')
        response = self.client.post(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_start_election_normal_user_login(self):
        """If user was not superuser, they do not have permission to start election."""
        self.client.force_login(self.users[1])
        self.test_url = reverse('api_election_list')
        response = self.client.post(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_start_election_super_user_login(self):
        """If user was superuser, they can start election."""
        self.election1.delete() # On going election
        self.client.force_login(self.users[4])
        self.test_url = reverse('api_election_list')
        # response = self.client.post(self.test_url)
        response = self.client.post(self.test_url)
        response_content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_content["result"]["id"], 4)
        self.assertEqual(response_content["result"]["name"], 'Test election9')
        self.assertEqual(response_content["result"]["description"], 'Test election')
        self.assertNotEqual(response_content["result"]["start_date"], None)
        self.assertNotEqual(response_content["result"]["end_date"], None)

    def test_update_election_not_login(self):
        """If user not login, they cannot edit any election."""
        self.test_url = reverse('api_election_list')
        response = self.client.put(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_election_normal_user_login(self):
        """If user was not superuser, they do not have permission to edit any election."""
        self.client.force_login(self.users[2])
        self.test_url = reverse('api_election_list')
        response = self.client.put(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_edit_election_super_user_login(self):
        """If user was superuser, they can start election."""
        self.client.force_login(self.users[4])
        self.test_url = reverse('api_election_list')
        response = self.client.put(self.test_url, {
            'election_id': 1,
            'description': 'First election'
        }, format='json')
        response_content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response_content), 2)
        self.assertEqual(response_content["result"]["id"], 1)
        self.assertEqual(response_content["result"]["name"], 'Test election1')
        self.assertEqual(response_content["result"]["description"], 'First election')
        self.assertNotEqual(response_content["result"]["start_date"], None)
        self.assertNotEqual(response_content["result"]["end_date"], None)

    def test_get_election_detail(self):
        """Test normal case of get election detail."""
        self.test_url = reverse('api_election_detail', args=[self.election1.id])
        response = self.client.get(self.test_url)
        response_content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_content["election"]), 6)
        self.assertEqual(response_content["election"]["id"], 1)
        self.assertEqual(response_content["election"]["name"], 'Test election1')
        self.assertNotEqual(response_content["election"]["start_date"], None)
        self.assertNotEqual(response_content["election"]["end_date"], None)

    def test_get_not_exist_election(self):
        """Test case of get detail on not exist election."""
        self.test_url = reverse('api_election_detail', args=[999])
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_not_exist_ongoing_election(self):
        """Test case for get ongoing election but there are no ongoing election."""
        # make election end
        self.election1.start_date -= timedelta(days=9)
        self.election1.end_date -= timedelta(days=7)
        self.election1.save()

        self.test_url = reverse('api_election_current')
        response = self.client.get(self.test_url)
        response_content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_content["errors"]["detail"],  'There are no ongoing election.')

    def test_get_ongoing_election(self):
        """Test case for get ongoing election."""
        self.test_url = reverse('api_election_current')
        response = self.client.get(self.test_url)
        response_content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_content["election"]), 6)
        self.assertEqual(response_content["election"]["id"], 1)
        self.assertEqual(response_content["election"]["name"], 'Test election1')
        self.assertNotEqual(response_content["election"]["start_date"], None)
        self.assertNotEqual(response_content["election"]["end_date"], None)

    def test_get_election_result_normal_user_login(self):
        """Test case for normal user get election result."""
        self.vote_url = reverse('api_election_vote', args=[self.election1.id])
        self.test_url = reverse('api_election_result_by_area', args=[self.election1.id, self.areas[0].id])
        self.client.force_login(self.users[3])
        self.client.post(self.vote_url)

        # make election end
        self.election1.start_date -= timedelta(days=9)
        self.election1.end_date -= timedelta(days=7)
        self.election1.save()

        response = self.client.get(self.test_url, {
            'area_id': self.areas[0].id,
            'elction_id': self.election1.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_election_result_super_user_login(self):
        """Test case for superuser get election result."""
        self.vote_url = reverse('api_election_vote', args=[self.election1.id])
        self.test_url = reverse('api_election_result_by_area', args=[self.election1.id, self.areas[0].id])
        self.client.force_login(self.users[4])
        self.client.post(self.vote_url)

        # make election end
        self.election1.start_date -= timedelta(days=9)
        self.election1.end_date -= timedelta(days=7)
        self.election1.save()

        response = self.client.get(self.test_url, {
            'area_id': self.areas[0].id,
            'elction_id': self.election1.id
        }, format='json')
        response_content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_content["detail"], 'Get election result successfully')
        self.assertEqual(response_content["vote_result"][0]["candidate"]["id"], self.candidates[0].id)
        self.assertEqual(response_content["vote_result"][0]["candidate"]["area"]["id"], self.areas[0].id)

    def test_get_not_exist_election_result(self):
        """Test case for get the result of non-exist election."""
        self.vote_url = reverse('api_election_vote', args=[self.election1.id])
        self.test_url = reverse('api_election_result_by_area', args=[999, self.areas[0].id])
        self.client.force_login(self.users[4])
        self.client.post(self.vote_url)

        # make election end
        self.election1.start_date -= timedelta(days=9)
        self.election1.end_date -= timedelta(days=7)
        self.election1.save()

        response = self.client.get(self.test_url, {
            'area_id': self.areas[0].id,
            'elction_id': self.election1.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_election_result_in_not_exist_area(self):
        """Test case for get the election result of non-exist area."""
        self.vote_url = reverse('api_election_vote', args=[self.election1.id])
        self.test_url = reverse('api_election_result_by_area', args=[self.election1.id, 999])
        self.client.force_login(self.users[4])
        self.client.post(self.vote_url)

        # make election end
        self.election1.start_date -= timedelta(days=9)
        self.election1.end_date -= timedelta(days=7)
        self.election1.save()

        response = self.client.get(self.test_url, {
            'area_id': self.areas[0].id,
            'elction_id': self.election1.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_ongoing_election_result(self):
        """Test case of get result ongoing election"""
        self.vote_url = reverse('api_election_vote', args=[self.election1.id])
        self.test_url = reverse('api_election_result_by_area', args=[self.election1.id, self.areas[0].id])
        self.client.force_login(self.users[3])
        self.client.post(self.vote_url)
        response = self.client.get(self.test_url, {
            'area_id': self.areas[0].id,
            'elction_id': self.election1.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
