from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('area', views.area_list, name='area_list'),
    path('area/add', views.add_area, name='add_area'),
    path('area/<int:area_id>', views.area_detail, name='area_detail'),
    path('area/<int:area_id>/edit', views.edit_area, name='edit_area'),
    path('candidate', views.candidate_list, name='candidate_list'),
    path('candidate/add', views.add_candidate, name='add_candidate'),
    path('candidate/<int:candidate_id>', views.candidate_detail, name='candidate_detail'),
    path('candidate/<int:candidate_id>/edit', views.edit_candidate, name='edit_candidate'),
    path('election', views.election_list, name='election_list'),
    path('election/add', views.start_election, name='start_election'),
    path('election/<int:election_id>', views.election_detail, name='election_detail'),
    path('election/<int:election_id>/edit', views.edit_election, name='edit_election'),
    path('election/<int:election_id>/vote', views.vote, name='vote'),
    path('election/<int:election_id>/history', views.vote_history, name='vote_history'),
    path('election/<int:election_id>/result', views.election_result, name='election_result'),
]
