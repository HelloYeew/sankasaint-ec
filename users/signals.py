from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import ColourSettings, LegacyProfile, NewProfile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        ColourSettings.objects.create(user=instance)
        LegacyProfile.objects.create(user=instance)
        NewProfile.objects.create(user=instance)
