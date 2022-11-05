from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_GET

import users.seed
from apps.forms import AreaForm, CandidateForm, StartElectionForm, EditElectionForm, CandidateVoteForm, PartyForm, \
    PartyVoteForm
from apps.models import LegacyArea, LegacyCandidate, LegacyElection, LegacyVote, LegacyParty, NewArea, NewCandidate, \
    NewElection, NewParty, VoteCheck, VoteResultCandidate, VoteResultParty
from apps.utils import check_election_status, get_sorted_election_result
from users.models import ColourSettings, UtilityMissionLog


@require_GET
def robots_txt(request):
    """
    Return the robots.txt file to tell the search engine crawlers not to index the site.
    """
    lines = [
        # Disallowed all robots
        "User-agent: *",
        "Disallow: /",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def homepage(request):
    """
    Homepage view that's normally show the current election information.
    """
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        ongoing_election_old = []
        ongoing_election_new = []
        for election in LegacyElection.objects.all().order_by('end_date'):
            if check_election_status(election) == 'Ongoing':
                ongoing_election_old.append(election)
        for election in NewElection.objects.all().order_by('end_date'):
            if check_election_status(election) == 'Ongoing':
                ongoing_election_new.append(election)
        return render(request, 'homepage.html', {
            'colour_settings': colour_settings,
            'ongoing_election_old': ongoing_election_old,
            'ongoing_election_new': ongoing_election_new,
        })
    else:
        return render(request, 'homepage.html')


def documentation(request):
    """
    A page that's include the link to API documentation.
    """
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'documentation.html', {
            'colour_settings': colour_settings
        })
    else:
        return render(request, 'documentation.html')


def area_list(request):
    """
    List all the NewArea objects in the database.
    """
    all_area_new = NewArea.objects.all().order_by('id')
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/area/area_list.html', {
            'colour_settings': colour_settings,
            'all_area_new': all_area_new
        })
    else:
        return render(request, 'apps/area/area_list.html', {
            'all_area_new': all_area_new
        })


def legacy_area_list(request):
    """
    A fallback page that's list all the LegacyArea objects in the database.

    We are not allowed to do the CRUD operation on the LegacyArea objects anymore, but we still need to show them.
    """
    all_area_legacy = LegacyArea.objects.all().order_by('id')
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/area/area_list_legacy.html', {
            'colour_settings': colour_settings,
            'all_area_legacy': all_area_legacy,
        })
    else:
        return render(request, 'apps/area/area_list_legacy.html', {
            'all_area_legacy': all_area_legacy,
        })


@login_required
def add_area(request):
    """
    Add a new area to the database.

    This view is only accessible to the staff or superuser.
    """
    if request.user.is_staff or request.user.is_superuser:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        if request.method == 'POST':
            form = AreaForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Area has been added!')
                return redirect('area_list')
        else:
            form = AreaForm()
        return render(request, 'apps/area/add_area.html', {
            'colour_settings': colour_settings,
            'form': form
        })
    else:
        messages.error(request, 'You are not authorised to access this page.')
        return redirect('area_list')


@login_required
def edit_area(request, area_id):
    """
    Edit an existing NewArea in the database.

    This view is only accessible to the staff or superuser.
    """
    if request.user.is_staff or request.user.is_superuser:
        try:
            area = NewArea.objects.get(id=area_id)
        except NewArea.DoesNotExist:
            messages.error(request, 'This area does not exist.')
            return redirect('area_list')
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        if request.method == 'POST':
            form = AreaForm(request.POST, instance=area)
            if form.is_valid():
                form.save()
                messages.success(request, 'Edit area successfully!')
                return redirect('area_list')
        else:
            form = AreaForm(instance=area)
        return render(request, 'apps/area/edit_area.html', {
            'colour_settings': colour_settings,
            'form': form,
            'area': area
        })
    else:
        messages.error(request, 'You are not authorised to access this page.')
        return redirect('area_list')


def area_detail_old(request, area_id):
    """
    Show the detail of a LegacyArea object.
    """
    try:
        area = LegacyArea.objects.get(id=area_id)
    except LegacyArea.DoesNotExist:
        messages.error(request, 'This area does not exist.')
        return redirect('area_list')
    available_candidate = LegacyCandidate.objects.filter(area=area).order_by('id')
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/area/area_detail_old.html', {
            'colour_settings': colour_settings,
            'area': area,
            'available_candidate': available_candidate
        })
    else:
        return render(request, 'apps/area/area_detail_old.html', {
            'area': area,
            'available_candidate': available_candidate
        })


def area_detail_new(request, area_id):
    """
    Show the detail of a NewArea object.
    """
    try:
        area = NewArea.objects.get(id=area_id)
    except NewArea.DoesNotExist:
        messages.error(request, 'This area does not exist.')
        return redirect('area_list')
    available_candidate = NewCandidate.objects.filter(area=area).order_by('id')
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/area/area_detail_new.html', {
            'colour_settings': colour_settings,
            'area': area,
            'available_candidate': available_candidate
        })
    else:
        return render(request, 'apps/area/area_detail_new.html', {
            'area': area,
            'available_candidate': available_candidate
        })


def candidate_list(request):
    """
    List all the NewCandidate objects in the database.
    """
    all_candidate_new = NewCandidate.objects.all().order_by('id')
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/candidate/candidate_list.html', {
            'colour_settings': colour_settings,
            'all_candidate_new': all_candidate_new
        })
    else:
        return render(request, 'apps/candidate/candidate_list.html', {
            'all_candidate_new': all_candidate_new
        })


def legacy_candidate_list(request):
    """
    A fallback page that's list all the LegacyCandidate objects in the database.

    We are not allowed to do the CRUD operation on the LegacyCandidate objects anymore, but we still need to show them.
    """
    all_candidate_legacy = LegacyCandidate.objects.all().order_by('id')
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/candidate/candidate_list_legacy.html', {
            'colour_settings': colour_settings,
            'all_candidate_legacy': all_candidate_legacy,
        })
    else:
        return render(request, 'apps/candidate/candidate_list_legacy.html', {
            'all_candidate_legacy': all_candidate_legacy,
        })


@login_required
def add_candidate(request):
    """
    Add a new candidate to the database.

    This view is only accessible to the staff or superuser.
    """
    if request.user.is_staff or request.user.is_superuser:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        if request.method == 'POST':
            form = CandidateForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Candidate has been added!')
                return redirect('candidate_list')
        else:
            form = CandidateForm()
        return render(request, 'apps/candidate/add_candidate.html', {
            'colour_settings': colour_settings,
            'form': form
        })
    else:
        messages.error(request, 'You are not authorised to access this page.')
        return redirect('homepage')


@login_required
def edit_candidate(request, candidate_id):
    """
    Edit an existing NewCandidate in the database.

    This view is only accessible to the staff or superuser.
    """
    if request.user.is_staff or request.user.is_superuser:
        try:
            candidate = NewCandidate.objects.get(id=candidate_id)
        except NewCandidate.DoesNotExist:
            messages.error(request, 'This candidate does not exist.')
            return redirect('candidate_list')
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        if request.method == 'POST':
            form = CandidateForm(request.POST, request.FILES, instance=candidate)
            if form.is_valid():
                form.save()
                messages.success(request, 'Edit candidate successfully!')
                return redirect('candidate_list')
        else:
            form = CandidateForm(instance=candidate)
        return render(request, 'apps/candidate/edit_candidate.html', {
            'colour_settings': colour_settings,
            'form': form,
            'candidate': candidate
        })
    else:
        messages.error(request, 'You are not authorised to access this page.')
        return redirect('homepage')


def candidate_detail_old(request, candidate_id):
    """
    Show the detail of a LegacyCandidate object.
    """
    try:
        candidate = LegacyCandidate.objects.get(id=candidate_id)
    except LegacyCandidate.DoesNotExist:
        messages.error(request, 'This candidate does not exist.')
        return redirect('candidate_list')
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/candidate/candidate_detail_old.html', {
            'colour_settings': colour_settings,
            'candidate': candidate
        })
    else:
        return render(request, 'apps/candidate/candidate_detail_old.html', {
            'candidate': candidate
        })


def candidate_detail_new(request, candidate_id):
    """
    Show the detail of a NewCandidate object.
    """
    try:
        candidate = NewCandidate.objects.get(id=candidate_id)
    except NewCandidate.DoesNotExist:
        messages.error(request, 'This candidate does not exist.')
        return redirect('candidate_list')
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/candidate/candidate_detail_new.html', {
            'colour_settings': colour_settings,
            'candidate': candidate
        })
    else:
        return render(request, 'apps/candidate/candidate_detail_new.html', {
            'candidate': candidate
        })


def election_list(request):
    """
    List all the NewElection objects in the database.
    """
    rendered_new_election = []
    for election in NewElection.objects.all().order_by('id'):
        rendered_new_election.append({
            'election': election,
            'status': check_election_status(election)
        })
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/election/election.html', {
            'colour_settings': colour_settings,
            'all_election_new': rendered_new_election
        })
    else:
        return render(request, 'apps/election/election.html', {
            'all_election_new': rendered_new_election
        })


def legacy_election_list(request):
    """
    A fallback page that's list all the LegacyElection objects in the database.

    We are not allowed to do the CRUD operation on the LegacyElection objects anymore, but we still need to show them.
    """
    rendered_legacy_election = []
    for election in LegacyElection.objects.all().order_by('id'):
        rendered_legacy_election.append({
            'election': election,
            'status': check_election_status(election)
        })
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/election/election_legacy.html', {
            'colour_settings': colour_settings,
            'all_election_legacy': rendered_legacy_election,
        })
    else:
        return render(request, 'apps/election/election_legacy.html', {
            'all_election_legacy': rendered_legacy_election,
        })


def election_detail_old(request, election_id):
    """
    Show the detail of a LegacyElection object.
    """
    try:
        election_object = LegacyElection.objects.get(id=election_id)
    except LegacyElection.DoesNotExist:
        messages.error(request, 'This election does not exist.')
        return redirect('election_list')
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        vote_history = LegacyVote.objects.filter(election=election_object, user=request.user).first()
        return render(request, 'apps/election/election_detail_old.html', {
            'colour_settings': colour_settings,
            'election': election_object,
            'status': check_election_status(election_object),
            'vote_history': vote_history
        })
    else:
        return render(request, 'apps/election/election_detail_old.html', {
            'election': election_object,
            'status': check_election_status(election_object),
        })


def election_detail_new(request, election_id):
    """
    Show the detail of a NewElection object.
    """
    try:
        election_object = NewElection.objects.get(id=election_id)
    except LegacyElection.DoesNotExist:
        messages.error(request, 'This election does not exist.')
        return redirect('election_list')
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/election/election_detail_new.html', {
            'colour_settings': colour_settings,
            'election': election_object,
            'status': check_election_status(election_object),
            'vote_history': VoteCheck.objects.filter(election=election_object, user=request.user).first()
        })
    else:
        return render(request, 'apps/election/election_detail_new.html', {
            'election': election_object,
            'status': check_election_status(election_object),
        })


@login_required
def start_election(request):
    """
    Start a new election by creating a NewElection object.

    This function is only accessible to the staff or superuser.
    """
    if request.user.is_staff or request.user.is_superuser:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        if request.method == 'POST':
            form = StartElectionForm(request.POST, request.FILES)
            if form.is_valid():
                election = form.save(commit=False)
                if not election.start_date:
                    election.start_date = timezone.now()
                election.save()
                messages.success(request, 'Election has been added!')
                return redirect('election_list')
        else:
            form = StartElectionForm()
        return render(request, 'apps/election/add_election.html', {
            'colour_settings': colour_settings,
            'form': form
        })
    else:
        messages.error(request, 'You are not authorised to access this page.')
        return redirect('homepage')


@login_required
def edit_election(request, election_id):
    """
    Edit an existing election.

    To make the election fair, we are only allowed to edit some non-essential fields only.
    """
    if request.user.is_staff or request.user.is_superuser:
        try:
            election = NewElection.objects.get(id=election_id)
        except LegacyElection.DoesNotExist:
            messages.error(request, 'This election does not exist.')
            return redirect('election_list')
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        if request.method == 'POST':
            form = EditElectionForm(request.POST, request.FILES, instance=election)
            if form.is_valid():
                form.save()
                messages.success(request, 'Edit election successfully!')
                return redirect('election_list')
        else:
            form = EditElectionForm(instance=election)
        return render(request, 'apps/election/edit_election.html', {
            'colour_settings': colour_settings,
            'form': form,
            'election': election
        })
    else:
        messages.error(request, 'You are not authorised to access this page.')
        return redirect('homepage')


@login_required
def vote(request, election_id):
    """
    Vote for a candidate for an election.
    """
    if request.user.newprofile.area is None:
        messages.error(request, 'Please contact administrator to set your area.')
        return redirect('election_detail_new', election_id=election_id)
    else:
        try:
            election = NewElection.objects.get(id=election_id)
        except NewElection.DoesNotExist:
            messages.error(request, 'This election does not exist.')
            return redirect('election_list')
        if check_election_status(election) == 'Ongoing':
            if not VoteCheck.objects.filter(election=election, user=request.user).exists():
                colour_settings = ColourSettings.objects.filter(user=request.user).first()
                if request.method == 'POST':
                    candidate_form = CandidateVoteForm(request.POST, area=request.user.newprofile.area)
                    party_form = PartyVoteForm(request.POST)
                    if candidate_form.is_valid() and party_form.is_valid():
                        # tally the candidate
                        if VoteResultCandidate.objects.filter(election=election, candidate=candidate_form.cleaned_data['candidate']).exists():
                            candidate = VoteResultCandidate.objects.get(election=election, candidate=candidate_form.cleaned_data['candidate'])
                            candidate.vote += 1
                            candidate.save()
                        else:
                            candidate = VoteResultCandidate.objects.create(election=election, candidate=candidate_form.cleaned_data['candidate'], vote=1)
                            candidate.save()
                        if VoteResultParty.objects.filter(election=election, party=party_form.cleaned_data['party']).exists():
                            party = VoteResultParty.objects.get(election=election, party=party_form.cleaned_data['party'])
                            party.vote += 1
                            party.save()
                        else:
                            party = VoteResultParty.objects.create(election=election, party=party_form.cleaned_data['party'], vote=1)
                            party.save()
                        # register this user as voted for this election
                        VoteCheck.objects.create(election=election, user=request.user)
                        messages.success(request, 'Vote has been submitted!')
                        return redirect('election_detail_new', election_id=election_id)
                else:
                    candidate_form = CandidateVoteForm(area=request.user.newprofile.area)
                    party_form = PartyVoteForm()
                return render(request, 'apps/vote/vote.html', {
                    'colour_settings': colour_settings,
                    'candidate_form': candidate_form,
                    'party_form': party_form,
                    'election': election
                })
            else:
                messages.error(request, 'You have already voted in this election.')
                return redirect('election_detail_new', election_id=election_id)
        elif check_election_status(election) == 'Upcoming':
            messages.error(request, 'This election has not started yet.')
            return redirect('election_detail_new', election_id=election_id)
        else:
            messages.error(request, 'This election has ended.')
            return redirect('election_detail_new', election_id=election_id)


@login_required
def vote_history(request, election_id):
    """
    Show the vote history of a user for an election.

    This page only show who already voted for this election, but not show what they voted for since we followed
    the black box voting system, and we are not collecting any information about who they voted for.
    """
    if request.user.is_staff or request.user.is_superuser:
        try:
            election = NewElection.objects.get(id=election_id)
        except NewElection.DoesNotExist:
            messages.error(request, 'This election does not exist.')
            return redirect('election_list')
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        election_vote_history = VoteCheck.objects.filter(election=election)
        return render(request, 'apps/vote/vote_history.html', {
            'colour_settings': colour_settings,
            'vote_history': election_vote_history,
            'election': election
        })
    else:
        messages.error(request, 'You are not authorised to access this page.')
        return redirect('homepage')


def election_result(request, election_id):
    """
    Show the election result of an election.

    TODO: Move this page to NewElection model.
    """
    try:
        election = LegacyElection.objects.get(id=election_id)
    except LegacyElection.DoesNotExist:
        messages.error(request, 'This election does not exist.')
        return redirect('election_list')
    if check_election_status(election) != 'Finished' and (
            request.user.is_staff or request.user.is_superuser) or check_election_status(election) == 'Finished':
        sorted_result = get_sorted_election_result(election)
        first_candidate = sorted_result[0]
        second_candidate = sorted_result[1]
        third_candidate = sorted_result[2]
        if request.user.is_authenticated:
            colour_settings = ColourSettings.objects.filter(user=request.user).first()
            return render(request, 'apps/vote/election_result.html', {
                'colour_settings': colour_settings,
                'first_candidate': first_candidate,
                'second_candidate': second_candidate,
                'third_candidate': third_candidate,
                'election': election
            })
        else:
            return render(request, 'apps/vote/election_result.html', {
                'first_candidate': first_candidate,
                'second_candidate': second_candidate,
                'third_candidate': third_candidate,
                'election': election
            })
    else:
        messages.error(request, 'This election has not ended yet.')
        return redirect('election_detail', election_id=election_id)


@login_required
def detailed_election_result(request, election_id):
    """
    Show the detailed election result of an election.

    TODO: Move this page to NewElection model.
    """
    try:
        election = LegacyElection.objects.get(id=election_id)
    except LegacyElection.DoesNotExist:
        messages.error(request, 'This election does not exist.')
        return redirect('election_list')
    if check_election_status(election) != 'Finished' and (
            request.user.is_staff or request.user.is_superuser) or check_election_status(election) == 'Finished':
        vote_result = get_sorted_election_result(election)
        if request.user.is_authenticated:
            colour_settings = ColourSettings.objects.filter(user=request.user).first()
            return render(request, 'apps/vote/detailed_election_result.html', {
                'colour_settings': colour_settings,
                'vote_result': vote_result,
                'election': election
            })
        else:
            return render(request, 'apps/vote/detailed_election_result.html', {
                'vote_result': vote_result,
                'election': election
            })
    else:
        messages.error(request, 'This election has not ended yet.')
        return redirect('election_detail', election_id=election_id)


def party_list(request):
    """
    Show the list of NewParty objects.
    """
    all_party_new = NewParty.objects.all().order_by('id')
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/party/party_list.html', {
            'colour_settings': colour_settings,
            'party_list_new': all_party_new
        })
    else:
        return render(request, 'apps/party/party_list.html', {
            'party_list_new': all_party_new
        })


def legacy_party_list(request):
    """
    A fallback page that's list all the LegacyParty objects in the database.

    We are not allowed to do the CRUD operation on the LegacyParty objects anymore, but we still need to show them.
    """
    all_party_old = LegacyParty.objects.all().order_by('id')
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/party/party_list_legacy.html', {
            'colour_settings': colour_settings,
            'party_list_old': all_party_old,
        })
    else:
        return render(request, 'apps/party/party_list_legacy.html', {
            'party_list_old': all_party_old
        })


@login_required
def add_party(request):
    """
    Add a new party to the database.
    """
    if request.user.is_staff or request.user.is_superuser:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        if request.method == 'POST':
            form = PartyForm(request.POST, request.FILES)
            if form.is_valid():
                party = form.save()
                party.save()
                messages.success(request, 'Party has been added!')
                return redirect('party_list')
        else:
            form = PartyForm()
        return render(request, 'apps/party/add_party.html', {
            'colour_settings': colour_settings,
            'form': form
        })
    else:
        messages.error(request, 'You are not authorised to access this page.')
        return redirect('homepage')


def edit_party(request, party_id):
    """
    Edit an existing party in the database.
    """
    if request.user.is_staff or request.user.is_superuser:
        try:
            party = NewParty.objects.get(id=party_id)
        except NewParty.DoesNotExist:
            messages.error(request, 'This party does not exist.')
            return redirect('party_list')
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        if request.method == 'POST':
            form = PartyForm(request.POST, request.FILES, instance=party)
            if form.is_valid():
                party = form.save()
                party.save()
                messages.success(request, 'Party has been updated!')
                return redirect('party_list')
        else:
            form = PartyForm(instance=party)
        return render(request, 'apps/party/edit_party.html', {
            'colour_settings': colour_settings,
            'form': form,
            'party': party
        })
    else:
        messages.error(request, 'You are not authorised to access this page.')
        return redirect('homepage')


def party_detail_old(request, party_id):
    """
    Show the detail of a LegacyParty object.
    """
    try:
        party = LegacyParty.objects.get(id=party_id)
    except LegacyParty.DoesNotExist:
        messages.error(request, 'This party does not exist.')
        return redirect('party_list')
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/party/party_detail_old.html', {
            'colour_settings': colour_settings,
            'party': party
        })
    else:
        return render(request, 'apps/party/party_detail_old.html', {
            'party': party
        })


def party_detail_new(request, party_id):
    """
    Show the detail of a NewParty object.
    """
    try:
        party = NewParty.objects.get(id=party_id)
    except NewParty.DoesNotExist:
        messages.error(request, 'This party does not exist.')
        return redirect('party_list')
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/party/party_detail_new.html', {
            'colour_settings': colour_settings,
            'party': party
        })
    else:
        return render(request, 'apps/party/party_detail_new.html', {
            'party': party
        })


@login_required()
def utils(request):
    """
    A utility menu for the staff and superuser.
    """
    if request.user.is_staff or request.user.is_superuser:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        utility_log = UtilityMissionLog.objects.all().order_by('id')
        return render(request, 'apps/utils/utils.html', {
            'colour_settings': colour_settings,
            'import_legacy_data': len(UtilityMissionLog.objects.filter(field='import_legacy_data', done=True)) > 0,
            'utility_log': utility_log,
            'users_list': User.objects.all().order_by('id')
        })
    else:
        messages.error(request, 'You are not authorised to access this page.')
        return redirect('homepage')


@login_required()
def import_legacy_data(request):
    """
    Import the legacy data from the old dump file to the new database.

    This menu normally can be accessed only once in the lifetime of the website and only can be accessed by the staff and superuser.
    """
    if request.user.is_staff or request.user.is_superuser:
        try:
            users.seed.seed_data()
            messages.success(request, 'Legacy data has been imported!')
            UtilityMissionLog.objects.create(
                user=request.user,
                field='import_legacy_data',
                done=True,
                description='Import legacy data successfully.'
            )
            return redirect('utils')
        except Exception as e:
            messages.error(request, 'Legacy data import failed : ' + str(e))
            users.models.UtilityMissionLog.objects.create(
                user=request.user,
                field='import_legacy_data',
                done=False,
                description='Import legacy data failed : ' + str(e)
            )
            return redirect('utils')
    else:
        messages.error(request, 'You are not authorised to access this function.')
        return redirect('homepage')
