from django.urls import path

from apis.views import *

urlpatterns = [
    path('login', LoginView.as_view(), name='api_login'),
    path('profile', UserProfileView.as_view(), name='api_profile'),
]