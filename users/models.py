from django.db import models
from colorfield.fields import ColorField
from django.contrib.auth.models import User

from apps.models import Area


class ColourSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    color_primary = ColorField(default='#DFD9D6')
    color_accent = ColorField(default='#DBC2D1')
    color_background = ColorField(default='#0A0A0A')
    mask_opacity = models.FloatField(default=0.5, max_length=1)

    def __str__(self):
        return self.user.username + '\'s colour settings'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(default='default_profile.png', upload_to='profile_pics')

    def __str__(self):
        return self.user.username + '\'s profile'