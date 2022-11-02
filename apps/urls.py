from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('docs/', views.documentation, name='documentation'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('area', views.area_list, name='area_list'),
    path('area/add', views.add_area, name='add_area'),
    path('area/<int:area_id>-legacy', views.area_detail_old, name='area_detail_old'),
    path('area/<int:area_id>', views.area_detail_new, name='area_detail_new'),
    path('area/<int:area_id>/edit', views.edit_area, name='edit_area'),
    path('candidate', views.candidate_list, name='candidate_list'),
    path('candidate/add', views.add_candidate, name='add_candidate'),
    path('candidate/<int:candidate_id>-legacy', views.candidate_detail_old, name='candidate_detail_old'),
    path('candidate/<int:candidate_id>', views.candidate_detail_new, name='candidate_detail_new'),
    path('candidate/<int:candidate_id>/edit', views.edit_candidate, name='edit_candidate'),
    path('election', views.election_list, name='election_list'),
    path('election/add', views.start_election, name='start_election'),
    path('election/<int:election_id>-legacy', views.election_detail_old, name='election_detail_old'),
    path('election/<int:election_id>', views.election_detail_new, name='election_detail_new'),
    path('election/<int:election_id>/edit', views.edit_election, name='edit_election'),
    path('election/<int:election_id>/vote', views.vote, name='vote'),
    path('election/<int:election_id>/history', views.vote_history, name='vote_history'),
    path('election/<int:election_id>/result', views.election_result, name='election_result'),
    path('election/<int:election_id>/detailed_result', views.detailed_election_result, name='detailed_election_result'),
    path('party', views.party_list, name='party_list'),
    path('party/add', views.add_party, name='add_party'),
    path('party/<int:party_id>-legacy', views.party_detail_old, name='party_detail_old'),
    path('party/<int:party_id>', views.party_detail_new, name='party_detail_new'),
    path('party/<int:party_id>/edit', views.edit_party, name='edit_party'),
    path('utils', views.utils, name='utils'),
    path('utils/legacy-import', views.import_legacy_data, name='import_legacy_data'),
]
