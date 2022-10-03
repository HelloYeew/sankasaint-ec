from django.urls import path

from apis.views import *

urlpatterns = [
    path('login', LoginView.as_view(), name='api_login'),
    path('profile', UserProfileView.as_view(), name='api_profile'),
    path('area', GetAllAreasView.as_view(), name='api_area_list'),
    path('candidate', GetAllCandidatesView.as_view(), name='api_candidate_list'),
    path('election', GetAllElectionsView.as_view(), name='api_election_list'),
]