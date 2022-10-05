"""ayaka URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from users import views as users_views

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Sankasaint EC API",
      default_version='v1',
      description="API for manage an election to select James Brucker as the next president of the United States of Sankasaint.",
      terms_of_service="https://youtu.be/eN6jkWxxm2Y?t=24",
      contact=openapi.Contact(email="me@helloyeew.dev"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    # path('signup/', users_views.signup, name='signup'),
    path('logout/', users_views.LogoutAndRedirect.as_view(), name='logout'),
    path('settings/', users_views.settings, name='settings'),
    path('profile/<int:user_id>/', users_views.profile, name='profile'),
    path('profile/edit', users_views.edit_profile, name='edit_profile'),
    path('', include('apps.urls')),
    path('api/', include('apis.urls')),
    # Swagger path
    re_path(r'^docs/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^docs/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^docs/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
