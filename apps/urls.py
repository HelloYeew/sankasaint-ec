from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('docs/', views.documentation, name='documentation'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('area', views.area_list, name='area_list'),
    path('area/add', views.add_area, name='add_area'),
    path('area/legacy', views.legacy_area_list, name='legacy_area_list'),
    path('area/legacy/<int:area_id>', views.area_detail_old, name='area_detail_old'),
    path('area/<int:area_id>', views.area_detail_new, name='area_detail_new'),
    path('area/<int:area_id>/edit', views.edit_area, name='edit_area'),
    path('candidate', views.candidate_list, name='candidate_list'),
    path('candidate/add', views.add_candidate, name='add_candidate'),
    path('candidate/legacy', views.legacy_candidate_list, name='legacy_candidate_list'),
    path('candidate/legacy/<int:candidate_id>', views.candidate_detail_old, name='candidate_detail_old'),
    path('candidate/<int:candidate_id>', views.candidate_detail_new, name='candidate_detail_new'),
    path('candidate/<int:candidate_id>/edit', views.edit_candidate, name='edit_candidate'),
    path('election', views.election_list, name='election_list'),
    path('election/legacy', views.legacy_election_list, name='legacy_election_list'),
    path('election/add', views.start_election, name='start_election'),
    path('election/legacy/<int:election_id>', views.election_detail_old, name='election_detail_old'),
    path('election/<int:election_id>', views.election_detail_new, name='election_detail_new'),
    path('election/<int:election_id>/edit', views.edit_election, name='edit_election'),
    path('election/<int:election_id>/vote', views.vote, name='vote'),
    path('election/<int:election_id>/history', views.vote_history, name='vote_history'),
    path('election/legacy/<int:election_id>/result', views.election_result, name='election_result'),
    path('election/<int:election_id>/detailed_result', views.detailed_election_result, name='detailed_election_result'),
    path('election/<int:election_id>/result', views.new_election_result, name='new_election_result'),
    path('election/<int:election_id>/result/area/<int:area_id>', views.new_election_result_by_area, name='new_election_result_by_area'),
    path('election/<int:election_id>/result/party', views.new_election_result_by_party, name='new_election_result_by_party'),
    path('party', views.party_list, name='party_list'),
    path('party/add', views.add_party, name='add_party'),
    path('party/legacy', views.legacy_party_list, name='legacy_party_list'),
    path('party/legacy/<int:party_id>', views.party_detail_old, name='party_detail_old'),
    path('party/<int:party_id>', views.party_detail_new, name='party_detail_new'),
    path('party/<int:party_id>/edit', views.edit_party, name='edit_party'),
    path('party/<int:party_id>/add', views.add_candidate_to_party, name='add_candidate_to_party'),
    path('party/<int:party_id>/remove/<int:candidate_id>', views.remove_candidate_from_party, name='remove_candidate_from_party'),
    path('utils', views.utils, name='utils'),
    path('utils/legacy-import', views.import_legacy_data, name='import_legacy_data'),
    path('partylist-calculation-detail', views.partylist_calculation_detail, name='partylist_calculation_detail'),
]
