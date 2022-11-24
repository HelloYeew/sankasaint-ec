import traceback

import requests
from django.contrib.auth.models import User
from django.core.management import BaseCommand

from apps.models import NewArea
from users.models import NewProfile


class Command(BaseCommand):
    help = 'Import population from government API'

    def handle(self, *args, **options):
        # fetch data from government API
        # TODO: Change to production API
        data = requests.get("https://catnip-api.herokuapp.com/api/v1/populations").json()
        self.stdout.write(self.style.SUCCESS('Found %s population data' % len(data)))
        # loop through data
        for population in data:
            try:
                # We use citizen ID as the username for the user so user can log in with their citizen ID
                user_in_database = User.objects.filter(username=str(population['citizenID'])).first()
                if user_in_database:
                    self.stdout.write(
                        self.style.SUCCESS('User "%s" already exists in database, updating...' % population['citizenID']))
                    user_in_database.username = population['citizenID']
                    user_in_database.first_name = population['firstName']
                    user_in_database.last_name = population['lastName']
                    user_in_database.save()
                    try:
                        user_profile = user_in_database.newprofile
                    except:
                        # create new profile
                        user_profile = NewProfile.objects.create(user=user_in_database)
                    user_profile.title = population['title']
                    user_profile.sex = population['sex']
                    user_profile.area = NewArea.objects.get(id=population['locationID'])
                    user_profile.right_to_vote = population['rightToVote']
                    user_profile.blacklist = population['blacklist']
                    user_profile.save()
                else:
                    self.stdout.write(self.style.SUCCESS('User with id "%s" not found in database, importing...' % population['citizenID']))
                    user = User.objects.create(
                        username=population['citizenID'],
                        first_name=population['firstName'],
                        last_name=population['lastName'],
                    )
                    user.save()
                    profile = user.newprofile
                    profile.title = population['title']
                    profile.sex = population['sex']
                    profile.area = NewArea.objects.get(id=population['locationID'])
                    profile.right_to_vote = population['rightToVote']
                    profile.blacklist = population['blacklist']
                    profile.save()
                    self.stdout.write(
                        self.style.SUCCESS(f"User {population['citizenID']} has been imported"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Cannot import user {population['citizenID']}: {e}"))
                # print full error to console
                traceback.print_exc()
        self.stdout.write(self.style.SUCCESS('Import population completed!'))
