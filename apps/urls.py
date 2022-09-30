from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('area', views.area_list, name='area_list'),
    path('area/add', views.add_area, name='add_area'),
    path('area/<int:area_id>', views.area_detail, name='area_detail'),
    path('area/<int:area_id>/edit', views.edit_area, name='edit_area'),
    path('candidate', views.candidate_list, name='candidate_list'),
    path('candidate/add', views.add_candidate, name='add_candidate'),
    path('candidate/<int:candidate_id>', views.candidate_detail, name='candidate_detail'),
    path('candidate/<int:candidate_id>/edit', views.edit_candidate, name='edit_candidate'),
]