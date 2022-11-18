from django.utils import timezone
from apps.models import LegacyElection, LegacyCandidate, LegacyVote, NewElection


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
    Return true if there is any on going election.
    """
    return NewElection.objects.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now()).exists()


def get_one_ongoing_election() -> NewElection:
    """
    Return on going election.

    This function assumes there is only one ongoing election.
    """
    return NewElection.objects.get(start_date__lte=timezone.now(), end_date__gte=timezone.now())