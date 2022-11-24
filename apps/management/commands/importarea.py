import traceback

import requests
from django.core.management import BaseCommand

from apps.models import NewArea


class Command(BaseCommand):
    help = 'Import election area from government API'

    def handle(self, *args, **options):
        # fetch data from government API
        # TODO: Change to production API
        data = requests.get("http://localhost:8080/api/area").json()
        self.stdout.write(self.style.SUCCESS('Found %s areas' % len(data)))
        # loop through data
        for area in data:
            try:
                area_in_database = NewArea.objects.filter(area_id=area['location_id'])
                if area_in_database:
                    self.stdout.write(
                        self.style.SUCCESS('Area "%s" already exists in database, updating...' % area['name']))
                    area_in_database.update(
                        id=area['location_id'],
                        name=area['location'],
                        population=area['population'],
                        number_of_voters=area['number_of_voters'],
                    )
                    area_in_database.save()
                else:
                    self.stdout.write(self.style.SUCCESS('Area with id "%s" not found in database, importing...' % area['location_id']))
                    NewArea.objects.create(
                        id=area['location_id'],
                        name=area['location'],
                        population=area['population'],
                        number_of_voters=area['number_of_voters'],
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"Area {area['location_id']} has been imported"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Cannot import area {area['location_id']}: {e}"))
                # print full error to console
                traceback.print_exc()
        self.stdout.write(self.style.SUCCESS('Import election area completed!'))
