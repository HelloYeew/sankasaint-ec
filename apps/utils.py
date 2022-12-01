import copy
from typing import Dict, List, Any

import math
from django.utils import timezone
from apps.models import LegacyElection, LegacyCandidate, LegacyVote, NewElection, VoteCheck, NewParty, VoteResultParty, \
    NewArea, VoteResultCandidate


def check_election_status(election: LegacyElection | NewElection) -> str:
    """
    Check the status of an election.

    This function can use for checking on both legacy and new election.

    :param election: The election to check.
    :return: The status of the election in string.
    :rtype: str
    """
    if election.start_date <= timezone.now():
        if election.end_date >= timezone.now():
            return 'Ongoing'
        else:
            return 'Finished'
    else:
        return 'Upcoming'


def get_sorted_election_result(election: LegacyElection) -> list:
    """
    Get the election result in a sorted list.

    This function is for calculate in LegacyElection model.

    :param election: The election to get the result.
    :return: The election result in a sorted list.
    :rtype: list
    """
    vote_result = []
    for candidate in LegacyCandidate.objects.all():
        vote_result.append({
            'candidate': candidate,
            'vote_count': LegacyVote.objects.filter(candidate=candidate, election=election).count()
        })
    vote_result = sorted(vote_result, key=lambda i: i['vote_count'], reverse=True)
    for i in range(len(vote_result)):
        vote_result[i]['rank'] = i + 1
    return vote_result


def is_there_ongoing_election() -> bool:
    """
    Return true if there is any ongoing election.
    """
    return NewElection.objects.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now()).exists()


def get_one_ongoing_election() -> NewElection:
    """
    Return an ongoing election.

    This function assumes there is only one ongoing election.
    """
    return NewElection.objects.get(start_date__lte=timezone.now(), end_date__gte=timezone.now())


def calculate_election_party_result(election_id: int) -> dict[
    str, list[dict[str, float | int | Any]] | list[dict[str, float | int | Any]] | dict[str, float | int | Any] | list[
        dict[str, float | int | Any]]]:
    """
    Calculate the election result for partylist.
    """
    election = NewElection.objects.get(id=election_id)
    # Get all user who vote in this election
    vote_per_seat = VoteCheck.objects.filter(election=election).count() / 500 if VoteCheck.objects.filter(
        election=election).count() > 0 else 0
    supposed_to_have_result = []
    for party in NewParty.objects.all():
        supposed_to_have_result.append({
            'party': party,
            'number': VoteResultParty.objects.filter(election=election,
                                                     party=party).count() / vote_per_seat if vote_per_seat else 0
        })
    real_result = copy.deepcopy(supposed_to_have_result)
    for result in real_result:
        # If the party has get first place in the election on the area on VoteResultCandidate,
        # minus that number from the supposed to have result
        for area in NewArea.objects.all():
            first_place = VoteResultCandidate.objects.filter(election=election, candidate__area_id=area.id).order_by(
                '-vote').first()
            if first_place and first_place.candidate.party == result['party']:
                result['number'] -= 1
    # Combine two list
    result = []
    for supposed, real in zip(supposed_to_have_result, real_result):
        result.append({
            'party': supposed['party'],
            'supposed_to_have': supposed['number'],
            'real': real['number']
        })
    # floor the result
    for party in result:
        party['supposed_to_have'] = math.floor(party['supposed_to_have'])
        party['real'] = math.floor(party['real'])
    # Add detail on number during calculation
    calculation_detail = {
        'vote_per_seat': vote_per_seat,
        'total_vote': VoteCheck.objects.filter(election=election).count()
    }
    # Sort the result by real number
    result = sorted(result, key=lambda k: k['real'], reverse=True)
    return {
        'supposed_to_have_result': supposed_to_have_result,
        'real_result': real_result,
        'result': result,
        'calculation_detail': calculation_detail,
    }
