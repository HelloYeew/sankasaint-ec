from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.models import Area, Candidate, Vote, Election
from users.models import Profile


class ProfileViewTest(TestCase):
    """Test case for profile page."""
    def setUp(self):
        """Create a dummy user"""
        self.user = User.objects.create_user(username='testuser', password='12345', email='testuser@test.com')
        self.user2 = User.objects.create_user(username='testuser2', password='12345', email='testuser2@test.com')
        self.area = Area.objects.create(name='testarea', description='testarea')
        self.candidate = Candidate.objects.create(name='testcandidate', description='testcandidate', area=self.area)
        self.election = Election.objects.create(name='testelection', description='testelection', start_date=timezone.now(), end_date=timezone.now())
        self.vote = Vote.objects.create(user=self.user, candidate=self.candidate, election=self.election)
        self.profile = Profile.objects.get(user=self.user)
        self.profile.area = self.area
        self.profile.save()
        self.url = reverse('profile', kwargs={'user_id': self.user.id})

    def test_profile_view_rendering(self):
        """Profile page must render correctly"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_profile_view_not_logged_in(self):
        """All edit button and vote history must be gone when see profile on not logged in."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Edit profile')
        self.assertNotContains(response, reverse('edit_profile'))
        self.assertNotContains(response, 'Vote history')
        # Check that the profile is rendered correctly
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'testuser@test.com')
        self.assertContains(response, 'testarea')

    def test_profile_view_logged_in_see_own_profile(self):
        """Edit button and vote history must be shown when see own profile."""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit profile')
        self.assertContains(response, reverse('edit_profile'))
        self.assertContains(response, 'Vote history')
        # Check that the profile is rendered correctly
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'testuser@test.com')
        self.assertContains(response, 'testarea')
        # Check that vote history is available
        self.assertContains(response, 'testelection')
        self.assertContains(response, 'testcandidate')
        self.assertContains(response, reverse('election_detail', kwargs={'election_id': self.election.id}))

    def test_profile_view_logged_in_see_other_profile(self):
        """Edit button and vote history must be gone when see other profile."""
        self.client.login(username='testuser2', password='12345')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Edit profile')
        self.assertNotContains(response, reverse('edit_profile'))
        self.assertNotContains(response, 'Vote history')
        # Check that the profile is rendered correctly
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'testuser@test.com')
        self.assertContains(response, 'testarea')