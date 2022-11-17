from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.models import LegacyArea, LegacyElection, LegacyCandidate, NewArea
from users.models import LegacyProfile


class HomepageTest(TestCase):
    """Test case for the homepage view."""
    def setUp(self):
        """Create a dummy user"""
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.url = reverse('homepage')

    def test_homepage_rendering(self):
        """Homepage must render correctly"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage.html')

    def test_homepage_view_not_login(self):
        """User must see only sign in text."""
        response = self.client.get(self.url)
        self.assertContains(response, 'Sign in')

    def test_homepage_view_login(self):
        """The homepage must see welcome text with the text tell to setup the area"""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.url)
        self.assertContains(response, f'Hello, {self.user.username} !')
        self.assertContains(response, 'You are not registered in any area.')

    def test_homepage_view_login_with_area(self):
        """User must see user's area information and blank list of ongoing election"""
        self.client.login(username='testuser', password='12345')
        area = LegacyArea.objects.create(name='test area', description='test area description')
        profile = LegacyProfile.objects.get(user=self.user)
        profile.area = area
        profile.save()
        response = self.client.get(self.url)
        self.assertContains(response, f'Hello, {self.user.username} !')
        self.assertContains(response, 'test area Detail')
        self.assertContains(response, 'No ongoing election.')
        self.assertContains(response, reverse('area_detail', kwargs={'area_id': area.id}))

    def test_homepage_view_login_with_area_and_ongoing_election(self):
        """User must see user's area information and ongoing election list"""
        self.client.login(username='testuser', password='12345')
        area = LegacyArea.objects.create(name='test area', description='test area description')
        profile = LegacyProfile.objects.get(user=self.user)
        profile.area = area
        profile.save()
        # Setup date using django timezone
        election = LegacyElection.objects.create(name='test election', description='test election description',
                                                 start_date=timezone.now() - timezone.timedelta(days=1),
                                                 end_date=timezone.now() + timezone.timedelta(days=1))
        response = self.client.get(self.url)
        self.assertContains(response, f'Hello, {self.user.username} !')
        self.assertContains(response, 'test area Detail')
        self.assertContains(response, 'test election')
        self.assertContains(response, 'test election description')
        self.assertContains(response, 'Started at ')
        # Find in response has a link to election detail
        self.assertContains(response, reverse('election_detail', kwargs={'election_id': election.id}))


class AreaListViewTest(TestCase):
    def setUp(self):
        """Set up dummy user and area"""
        self.url = reverse('area_list')
        self.user = User.objects.create_user(username='testuser', password='12345')
        # Add 3 dummy area
        self.area1 = NewArea.objects.create(name='test area 1', description='test area 1 description')
        self.area2 = NewArea.objects.create(name='test area 2', description='test area 2 description')
        self.area3 = NewArea.objects.create(name='test area 3', description='test area 3 description')

    def test_area_list_view_rendering(self):
        """Area list must render correctly"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'apps/area/area_list.html')

    def test_area_list_view_not_login(self):
        """User must see the list but not have the create and edit button."""
        response = self.client.get(self.url)
        self.assertContains(response, 'test area 1')
        self.assertContains(response, 'test area 2')
        self.assertContains(response, 'test area 3')
        self.assertContains(response, 'Detail')
        self.assertContains(response, reverse('area_detail_new', kwargs={'area_id': self.area1.id}))
        self.assertContains(response, reverse('area_detail_new', kwargs={'area_id': self.area2.id}))
        self.assertContains(response, reverse('area_detail_new', kwargs={'area_id': self.area3.id}))
        self.assertNotContains(response, 'Add area')
        self.assertNotContains(response, 'Edit')

    def test_area_list_view_login(self):
        """User that's not superuser and staff must see the list like not login"""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.url)
        self.assertContains(response, 'test area 1')
        self.assertContains(response, 'test area 2')
        self.assertContains(response, 'test area 3')
        self.assertContains(response, 'Detail')
        self.assertContains(response, reverse('area_detail_new', kwargs={'area_id': self.area1.id}))
        self.assertContains(response, reverse('area_detail_new', kwargs={'area_id': self.area2.id}))
        self.assertContains(response, reverse('area_detail_new', kwargs={'area_id': self.area3.id}))
        self.assertNotContains(response, 'Add area')
        self.assertNotContains(response, 'Edit')

    def test_area_list_view_login_staff(self):
        """User that's staff must see the list with create and edit button."""
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.url)
        self.assertContains(response, 'test area 1')
        self.assertContains(response, 'test area 2')
        self.assertContains(response, 'test area 3')
        self.assertContains(response, 'Detail')
        self.assertContains(response, reverse('area_detail_new', kwargs={'area_id': self.area1.id}))
        self.assertContains(response, reverse('area_detail_new', kwargs={'area_id': self.area2.id}))
        self.assertContains(response, reverse('area_detail_new', kwargs={'area_id': self.area3.id}))
        self.assertContains(response, 'Add area')
        self.assertContains(response, 'Edit')
        self.assertContains(response, reverse('add_area'))
        self.assertContains(response, reverse('edit_area', kwargs={'area_id': self.area1.id}))
        self.assertContains(response, reverse('edit_area', kwargs={'area_id': self.area2.id}))
        self.assertContains(response, reverse('edit_area', kwargs={'area_id': self.area3.id}))


class AreaDetailViewTest(TestCase):
    def setUp(self):
        """Set up dummy user and area"""
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.area = NewArea.objects.create(name='test area', description='test area description')
        self.url = reverse('area_detail_new', kwargs={'area_id': self.area.id})

    def test_area_detail_view_rendering(self):
        """Area detail must render correctly"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'apps/area/area_detail_new.html')

    def test_area_detail_view_not_login(self):
        """User must see the area detail but not have the edit button."""
        response = self.client.get(self.url)
        self.assertContains(response, 'Description')
        self.assertContains(response, 'test area')
        self.assertContains(response, 'Available Candidate')
        self.assertContains(response, 'No available candidate in this area.')
        self.assertNotContains(response, 'Edit')

    def test_area_detail_view_login(self):
        """User that's not superuser and staff must see the area detail like not login"""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.url)
        self.assertContains(response, 'Description')
        self.assertContains(response, 'test area')
        self.assertContains(response, 'Available Candidate')
        self.assertContains(response, 'No available candidate in this area.')
        self.assertNotContains(response, 'Edit')

    def test_area_detail_view_login_staff(self):
        """User that's staff must see the area detail with edit button."""
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.url)
        self.assertContains(response, 'Description')
        self.assertContains(response, 'test area')
        self.assertContains(response, 'Available Candidate')
        self.assertContains(response, 'No available candidate in this area.')
        self.assertContains(response, 'Edit')
        self.assertContains(response, reverse('edit_area', kwargs={'area_id': self.area.id}))

    def test_area_detail_view_with_candidate_not_login(self):
        """User must see the candidate in the area detail."""
        candidate1 = LegacyCandidate.objects.create(name='test candidate 1', description='test candidate description 1',
                                                    area=self.area)
        candidate2 = LegacyCandidate.objects.create(name='test candidate 2', description='test candidate description 2',
                                                    area=self.area)
        response = self.client.get(self.url)
        self.assertContains(response, 'Description')
        self.assertContains(response, 'test area')
        self.assertContains(response, 'Available Candidate')
        self.assertContains(response, 'test candidate 1')
        self.assertContains(response, 'test candidate 2')
        self.assertContains(response, reverse('candidate_detail', kwargs={'candidate_id': candidate1.id}))
        self.assertContains(response, reverse('candidate_detail', kwargs={'candidate_id': candidate2.id}))
        self.assertNotContains(response, reverse('edit_candidate', kwargs={'candidate_id': candidate1.id}))
        self.assertNotContains(response, reverse('edit_candidate', kwargs={'candidate_id': candidate2.id}))
        self.assertNotContains(response, 'No available candidate in this area.')
        self.assertNotContains(response, 'Edit')

    def test_area_detail_view_with_candidate_login(self):
        """User that's not superuser and staff must see the candidate in the area detail like not login."""
        self.client.login(username='testuser', password='12345')
        candidate1 = LegacyCandidate.objects.create(name='test candidate 1', description='test candidate description 1',
                                                    area=self.area)
        candidate2 = LegacyCandidate.objects.create(name='test candidate 2', description='test candidate description 2',
                                                    area=self.area)
        response = self.client.get(self.url)
        self.assertContains(response, 'Description')
        self.assertContains(response, 'test area')
        self.assertContains(response, 'Available Candidate')
        self.assertContains(response, 'test candidate 1')
        self.assertContains(response, 'test candidate 2')
        self.assertContains(response, reverse('candidate_detail', kwargs={'candidate_id': candidate1.id}))
        self.assertContains(response, reverse('candidate_detail', kwargs={'candidate_id': candidate2.id}))
        self.assertNotContains(response, reverse('edit_candidate', kwargs={'candidate_id': candidate1.id}))
        self.assertNotContains(response, reverse('edit_candidate', kwargs={'candidate_id': candidate2.id}))
        self.assertNotContains(response, 'No available candidate in this area.')
        self.assertNotContains(response, 'Edit')

    def test_area_detail_view_with_candidate_login_staff(self):
        """User that's staff must see the candidate in the area detail with edit button."""
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='12345')
        candidate1 = LegacyCandidate.objects.create(name='test candidate 1', description='test candidate description 1',
                                                    area=self.area)
        candidate2 = LegacyCandidate.objects.create(name='test candidate 2', description='test candidate description 2',
                                                    area=self.area)
        response = self.client.get(self.url)
        self.assertContains(response, 'Description')
        self.assertContains(response, 'test area')
        self.assertContains(response, 'Available Candidate')
        self.assertContains(response, 'test candidate 1')
        self.assertContains(response, 'test candidate 2')
        self.assertContains(response, 'Edit')
        self.assertContains(response, reverse('candidate_detail', kwargs={'candidate_id': candidate1.id}))
        self.assertContains(response, reverse('candidate_detail', kwargs={'candidate_id': candidate2.id}))
        self.assertContains(response, reverse('edit_candidate', kwargs={'candidate_id': candidate1.id}))
        self.assertContains(response, reverse('edit_candidate', kwargs={'candidate_id': candidate2.id}))
        self.assertNotContains(response, 'No available candidate in this area.')

    def test_area_detail_view_not_found(self):
        """Area not found must redirect to area list page."""
        url = reverse('area_detail', kwargs={'area_id': 999})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('area_list'))
        # Check that Django messages are set
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'This area does not exist.')


