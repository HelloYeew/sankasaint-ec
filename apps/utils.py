from django.utils import timezone
from apps.models import LegacyElection, LegacyCandidate, LegacyVote


def check_election_status(election: LegacyElection) -> str:
    if election.start_date <= timezone.now():
        if election.end_date >= timezone.now():
            return 'Ongoing'
        else:
            return 'Finished'
    else:
        return 'Upcoming'


def get_sorted_election_result(election: LegacyElection) -> list:
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

