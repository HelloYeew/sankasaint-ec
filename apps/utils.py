from django.utils import timezone
from apps.models import Election, Candidate, Vote


def check_election_status(election: Election) -> str:
    if election.start_date <= timezone.now():
        if election.end_date >= timezone.now():
            return 'Ongoing'
        else:
            return 'Finished'
    else:
        return 'Upcoming'


def get_sorted_election_result(election: Election) -> list:
    vote_result = []
    for candidate in Candidate.objects.all():
        vote_result.append({
            'candidate': candidate,
            'vote_count': Vote.objects.filter(candidate=candidate, election=election).count()
        })
    vote_result = sorted(vote_result, key=lambda i: i['vote_count'], reverse=True)
    for i in range(len(vote_result)):
        vote_result[i]['rank'] = i + 1
    return vote_result

