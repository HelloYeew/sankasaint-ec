import traceback

import requests
from django.contrib.auth.models import User
from django.core.management import BaseCommand

from apps.models import NewArea


class Command(BaseCommand):
    help = 'Import population from government API'

    def handle(self, *args, **options):
        # fetch data from government API
        # TODO: Change to production API
        data = requests.get("http://localhost:8080/api/population").json()
        self.stdout.write(self.style.SUCCESS('Found %s population data' % len(data)))
        # loop through data
        for population in data:
            try:
                # We use citizen ID as the username for the user so user can log in with their citizen ID
                user_in_database = User.objects.get(username=population['citizen_id'])
                if user_in_database:
                    self.stdout.write(
                        self.style.SUCCESS('User "%s" already exists in database, updating...' % population['citizen_id']))
                    user_in_database.update(
                        username=population['citizen_id'],
                        first_name=population['firstName'],
                        last_name=population['lastName'],
                    )
                    user_in_database.save()
                    user_profile = user_in_database.newprofile
                    user_profile.update(
                        title=population['title'],
                        area=NewArea.objects.get(area_id=population['locationID']),
                        right_to_vote=population['rightToVote'],
                        blacklist=population['blacklist']
                    )
                    user_profile.save()
                else:
                    self.stdout.write(self.style.SUCCESS('User with id "%s" not found in database, importing...' % population['citizen_id']))
                    user = User.objects.create(
                        username=population['citizen_id'],
                        first_name=population['firstName'],
                        last_name=population['lastName'],
                    )
                    user.save()
                    user.newprofile.update(
                        title=population['title'],
                        area=NewArea.objects.get(area_id=population['locationID']),
                        right_to_vote=population['rightToVote'],
                        blacklist=population['blacklist']
                    )
                    user.newprofile.save()
                    self.stdout.write(
                        self.style.SUCCESS(f"User {population['citizen_id']} has been imported"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Cannot import user {population['citizen_id']}: {e}"))
                # print full error to console
                traceback.print_exc()
        self.stdout.write(self.style.SUCCESS('Import population completed!'))