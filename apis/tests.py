from datetime import timedelta
from http.client import UNAUTHORIZED

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.models import NewElection, NewCandidate, NewArea, NewParty, VoteResultParty, VoteResultCandidate, VoteCheck
from django.utils import timezone


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
        response = self.client.post(self.test_url, {
            'candidate_id': self.candidates[0].id,
            'party_id': self.parties[0].id
        }, format='json')
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
        response = self.client.post(self.test_url, {
            'candidate_id': self.candidates[0].id,
            'party_id': self.parties[0].id,
        })
        self.assertEqual(response.status_code, UNAUTHORIZED)

    def test_vote_multiple_time(self):
        """
        Voting multiple times is not allowed.
        """
        self.client.force_login(self.users[0])
        VoteCheck.objects.create(user=self.users[0], election=self.election)
        response = self.client.post(self.test_url, {
            # Change candidate does not change expected result
            'candidate_id': self.candidates[1].id,
            'party_id': self.parties[0].id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_vote_invalid_party(self):
        """Voting invalid party should not be possible"""
        self.client.force_login(self.users[1])
        response = self.client.post(self.test_url, {
            'candidate_id': self.candidates[0].id,
            'party_id': 99999999
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(VoteCheck.objects.filter(user=self.users[1], election=self.election).exists())

    def test_vote_invalid_candidate(self):
        """Voting invalid candidate should not be possileb."""
        self.client.force_login(self.users[1])
        response = self.client.post(self.test_url, {
            'candidate_id': 9999999,
            'party_id': self.parties[0].id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(VoteCheck.objects.filter(user=self.users[1], election=self.election).exists())

    def test_vote_wrong_time(self):
        """Both upcoming and ended elections cannot be voted."""
        self.client.force_login(self.users[0])

        # Ended
        self.election.start_date -= timedelta(days=9)
        self.election.end_date -= timedelta(days=2)
        self.election.save()

        response = self.client.post(self.test_url, {
            'candidate_id': self.candidates[0].id,
            'party_id': self.parties[0].id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg="Ended election should not be voted")
        self.assertFalse(VoteCheck.objects.filter(user=self.users[0], election=self.election).exists())

        # Upcoming
        self.election.end_date += timedelta(days=21)
        self.election.start_date += timedelta(days=10)
        self.election.save()
        response = self.client.post(self.test_url, {
            'candidate_id': self.candidates[0].id,
            'party_id': self.parties[0].id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg="Upcoming election should not be voted")
        self.assertFalse(VoteCheck.objects.filter(user=self.users[0], election=self.election).exists())

    def test_vote_outside_area(self):
        """Voting candidate is only allowed in the same area."""
        self.client.force_login(self.users[3])
        response = self.client.post(self.test_url, {
            'candidate_id': self.candidates[0].id,
            'party_id': self.parties[1].id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg="Cannot vote outside area")
        self.assertFalse(VoteCheck.objects.filter(user=self.users[3], election=self.election).exists())

    def test_vote_without_area(self):
        """If user does not have area, there should be a warning."""
        self.client.force_login(self.users[0])
        self.areas[0].newprofile_set.remove(self.users[0].newprofile)
        self.areas[0].save()
        response = self.client.post(self.test_url, {
            'candidate_id': self.candidates[0].id,
            'party_id': self.parties[1].id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg="Must handle no area case")
        self.assertFalse(VoteCheck.objects.filter(user=self.users[0], election=self.election).exists())


class PartyApiTest(APITestCase):
    def setUp(self) -> None:
        """
        Create user for test party api
        """
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

        self.url = reverse('api_party_list')
        self.urls = reverse('api_party_detail', kwargs={'party_id': 1})

    def test_get_has_party(self):
        """User who has party should be able to see party list."""
        self.client.force_login(self.users[0])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_party_detail_found(self):
        """Party detail should be found."""
        self.client.force_login(self.users[0])
        response = self.client.get(self.urls)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_party_detail_not_found(self):
        """Party detail should not be found."""
        self.client.force_login(self.users[0])
        response = self.client.get(reverse('api_party_detail', kwargs={'party_id': 3}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
