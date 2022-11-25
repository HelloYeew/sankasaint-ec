import traceback

import requests
from django.core.management import BaseCommand

from apps.models import NewArea


class Command(BaseCommand):
    help = 'Import election area from government API'

    def handle(self, *args, **options):
        # fetch data from government API
        # TODO: Change to production API
        data = requests.get("https://catnip-api.herokuapp.com/api/v1/locations").json()
        print(data)
        self.stdout.write(self.style.SUCCESS('Found %s areas' % len(data)))
        # loop through data
        for area in data:
            try:
                area_in_database = NewArea.objects.filter(id=area['locationID']).first()
                if area_in_database:
                    self.stdout.write(
                        self.style.SUCCESS('Area "%s" already exists in database, updating...' % area['location']))
                    area_in_database.id = area['locationID']
                    area_in_database.name = area['location']
                    area_in_database.population = area['population']
                    area_in_database.number_of_voters = area['numberOfVoters']
                    area_in_database.save()
                else:
                    self.stdout.write(self.style.SUCCESS('Area with id "%s" not found in database, importing...' % area['locationID']))
                    NewArea.objects.create(
                        id=area['locationID'],
                        name=area['location'],
                        population=area['population'],
                        number_of_voters=area['numberOfVoters'],
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"Area {area['locationID']} has been imported"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Cannot import area {area['locationID']}: {e}"))
                # print full error to console
                traceback.print_exc()
        self.stdout.write(self.style.SUCCESS('Import election area completed!'))
