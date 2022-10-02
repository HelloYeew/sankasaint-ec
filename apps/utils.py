from django.utils import timezone
from apps.models import Election


def check_election_status(election: Election) -> str:
    if election.start_date <= timezone.now():
        if election.end_date >= timezone.now():
            return 'Ongoing'
        else:
            return 'Finished'
    else:
        return 'Upcoming'
