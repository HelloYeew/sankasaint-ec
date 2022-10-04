from django.urls import path

from apis.views import *

urlpatterns = [
    path('login', LoginView.as_view(), name='api_login'),
    path('profile', UserProfileView.as_view(), name='api_profile'),
    path('area', AreasView.as_view(), name='api_area_list'),
    path('candidate', CandidatesView.as_view(), name='api_candidate_list'),
    path('election', ElectionsView.as_view(), name='api_election_list'),
]