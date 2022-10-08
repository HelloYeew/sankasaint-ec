from django.urls import path

from apis.views import *

urlpatterns = [
    path('login', LoginView.as_view(), name='api_login'),
    path('profile', UserProfileView.as_view(), name='api_profile'),
    path('area', AreasView.as_view(), name='api_area_list'),
    path('area/<int:area_id>', AreaDetailView.as_view(), name='api_area_detail'),
    path('candidate', CandidatesView.as_view(), name='api_candidate_list'),
    path('candidate/<int:candidate_id>', CandidateDetailView.as_view(), name='api_candidate_detail'),
    path('election', ElectionsView.as_view(), name='api_election_list'),
    path('election/<int:election_id>', ElectionDetailView.as_view(), name='api_election_detail'),
]