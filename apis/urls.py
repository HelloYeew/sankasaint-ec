from django.urls import path

# NOTE: THIS IS ONLY TEMPORARY FIX. IT MUST BE ADDRESSED LATER
from django.views.decorators.csrf import csrf_exempt

from apis.views import *

urlpatterns = [
    # Remove login view as it is not used anymore.
    # path('login', csrf_exempt(LoginView.as_view()), name='api_login'),
    # path('logout', LogoutView.as_view(), name='api_logout'),
    path('profile', UserProfileView.as_view(), name='api_profile'),
    path('area', AreasView.as_view(), name='api_area_list'),
    path('area/<int:area_id>', AreaDetailView.as_view(), name='api_area_detail'),
    path('candidate', CandidatesView.as_view(), name='api_candidate_list'),
    path('candidate/<int:candidate_id>', CandidateDetailView.as_view(), name='api_candidate_detail'),
    path('election', ElectionsView.as_view(), name='api_election_list'),
    path('election/current', ElectionCurrentView.as_view(), name='api_election_current'),
    path('election/<int:election_id>', ElectionDetailView.as_view(), name='api_election_detail'),
    path('election/<int:election_id>/vote', ElectionVoteView.as_view(), name='api_election_vote'),
    path('party', PartyView.as_view(), name='api_party_list'),
    path('party/<int:party_id>', PartyDetailView.as_view(), name='api_party_detail'),
    path('election/<int:election_id>/result/party', ElectionResultByPartyView.as_view(), name='api_election_result_by_party'),
    path('election/<int:election_id>/result/party/raw', RawElectionResultByPartyView.as_view(), name='api_raw_election_result_by_party'),
    path('election/<int:election_id>/result/area/<int:area_id>', ElectionResultByAreaView.as_view(), name='api_election_result_by_area'),
    path('election/latest', ElectionLatestView.as_view(), name='api_latest_election'),
    path('election/latest/result/party', LatestElectionResultByPartyView.as_view(), name='api_latest_election_result_by_party'),
    path('election/latest/result/party/raw', LatestRawElectionResultByPartyView.as_view(), name='api_latest_raw_election_result_by_party'),
    path('election/latest/result/area/<int:area_id>', LatestElectionResultByAreaView.as_view(), name='api_latest_election_result_by_area'),
]