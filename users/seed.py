import json
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from apps.models import NewArea, NewElection, NewParty, NewCandidate, LegacyArea
from users.models import NewProfile, LegacyProfile


def seed_data():
    """
    Seed the old dump data into the new database.
    """
    file = []
    with open('seed/apps.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
        for p in data:
            file.append(p)
    candidate_for_import = []
    area_for_import = []
    election_for_import = []
    party_for_import = []
    for i in file:
        if i['model'] == 'apps.legacycandidate':
            candidate_for_import.append(i)
        elif i['model'] == 'apps.legacyarea':
            area_for_import.append(i)
        elif i['model'] == 'apps.legacyelection':
            election_for_import.append(i)
        elif i['model'] == 'apps.legacyparty':
            party_for_import.append(i)
    for i in range(len(area_for_import)):
        area_for_import[i] = {
            'name': area_for_import[i]['fields']['name']
        }
    for i in range(len(election_for_import)):
        election_for_import[i] = {
            'name': election_for_import[i]['fields']['name'],
            'description': election_for_import[i]['fields']['description'],
            'front_image': election_for_import[i]['fields']['front_image'],
            'start_date': election_for_import[i]['fields']['start_date'],
            'end_date': election_for_import[i]['fields']['end_date']
        }
    for i in range(len(party_for_import)):
        party_for_import[i] = {
            'name': party_for_import[i]['fields']['name'],
            'description': party_for_import[i]['fields']['description'],
            'image': party_for_import[i]['fields']['image'],
            'candidates': party_for_import[i]['fields']['candidates']
        }
    print(candidate_for_import)
    for i in range(len(candidate_for_import)):
        candidate_for_import[i] = {
            'username': candidate_for_import[i]['fields']['name'],
            'email': candidate_for_import[i]['fields']['name'] + '@genshin.com',
            'first_name': candidate_for_import[i]['fields']['name'],
            'last_name': "Irido",
            'password': make_password(candidate_for_import[i]['fields']['name'], salt=None, hasher='default'),
            'description': candidate_for_import[i]['fields']['description'],
            'area': candidate_for_import[i]['fields']['area'],
            'image': candidate_for_import[i]['fields']['image']
        }

    for i in area_for_import:
        NewArea.objects.create(**i)
    for i in election_for_import:
        NewElection.objects.create(**i)
    for i in party_for_import:
        NewParty.objects.create(
            # import everything except candidates
            **{k: v for k, v in i.items() if k != 'candidates'}
        )
    for i in candidate_for_import:
        User.objects.create(
            # import everything except description and area
            **{k: v for k, v in i.items() if k != 'description' and k != 'area' and k != 'image'}
        )
        NewCandidate.objects.create(
            user=User.objects.get(username=i['username']),
            image=i['image'],
            description=i['description'],
            area=NewArea.objects.get(id=i['area'])
        )
        # Update the user's area in the old and new profile
        user = User.objects.get(username=i['username'])
        new_profile = NewProfile.objects.get(user=user)
        legacy_profile = LegacyProfile.objects.get(user=user)
        new_profile.area = NewArea.objects.get(id=i['area'])
        legacy_profile.area = LegacyArea.objects.get(id=i['area'])
        new_profile.save()
        legacy_profile.save()
    