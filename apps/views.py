from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_GET

import users.seed
from apps.forms import AreaForm, CandidateForm, StartElectionForm, EditElectionForm, VoteForm, PartyForm
from apps.models import LegacyArea, LegacyCandidate, LegacyElection, LegacyVote, LegacyParty, NewArea, NewCandidate, \
    NewElection, NewParty
from apps.utils import check_election_status, get_sorted_election_result
from users.models import ColourSettings, UtilityMissionLog


@require_GET
def robots_txt(request):
    lines = [
        # Disallowed all robots
        "User-agent: *",
        "Disallow: /",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def homepage(request):
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        ongoing_election_old = []
        ongoing_election_new = []
        for election in LegacyElection.objects.all():
            if check_election_status(election) == 'Ongoing':
                ongoing_election_old.append(election)
        for election in NewElection.objects.all():
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
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'documentation.html', {
            'colour_settings': colour_settings
        })
    else:
        return render(request, 'documentation.html')


def area_list(request):
    all_area_legacy = LegacyArea.objects.all()
    all_area_new = NewArea.objects.all()
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/area/area_list.html', {
            'colour_settings': colour_settings,
            'all_area_legacy': all_area_legacy,
            'all_area_new': all_area_new
        })
    else:
        return render(request, 'apps/area/area_list.html', {
            'all_area_legacy': all_area_legacy,
            'all_area_new': all_area_new
        })


@login_required
def add_area(request):
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
        return redirect('homepage')


@login_required
def edit_area(request, area_id):
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
        return redirect('homepage')


def area_detail_old(request, area_id):
    try:
        area = LegacyArea.objects.get(id=area_id)
    except LegacyArea.DoesNotExist:
        messages.error(request, 'This area does not exist.')
        return redirect('area_list')
    available_candidate = LegacyCandidate.objects.filter(area=area)
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
    try:
        area = NewArea.objects.get(id=area_id)
    except NewArea.DoesNotExist:
        messages.error(request, 'This area does not exist.')
        return redirect('area_list')
    available_candidate = NewCandidate.objects.filter(area=area)
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
    all_candidate_legacy = LegacyCandidate.objects.all()
    all_candidate_new = NewCandidate.objects.all()
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/candidate/candidate_list.html', {
            'colour_settings': colour_settings,
            'all_candidate_legacy': all_candidate_legacy,
            'all_candidate_new': all_candidate_new
        })
    else:
        return render(request, 'apps/candidate/candidate_list.html', {
            'all_candidate_legacy': all_candidate_legacy,
            'all_candidate_new': all_candidate_new
        })


@login_required
def add_candidate(request):
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
    rendered_legacy_election = []
    rendered_new_election = []
    for election in LegacyElection.objects.all():
        rendered_legacy_election.append({
            'election': election,
            'status': check_election_status(election)
        })
    for election in NewElection.objects.all():
        rendered_new_election.append({
            'election': election,
            'status': check_election_status(election)
        })
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/election/election.html', {
            'colour_settings': colour_settings,
            'all_election_legacy': rendered_legacy_election,
            'all_election_new': rendered_new_election
        })
    else:
        return render(request, 'apps/election/election.html', {
            'all_election_legacy': rendered_legacy_election,
            'all_election_new': rendered_new_election
        })


def election_detail_old(request, election_id):
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
            'status': check_election_status(election_object)
        })
    else:
        return render(request, 'apps/election/election_detail_new.html', {
            'election': election_object,
            'status': check_election_status(election_object),
        })


@login_required
def start_election(request):
    if request.user.is_staff or request.user.is_superuser:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        if request.method == 'POST':
            form = StartElectionForm(request.POST, request.FILES)
            if form.is_valid():
                # to prevent error from database, if start_date is not set, set it to today
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
    if request.user.legacyprofile.area is None:
        messages.error(request, 'Please contact administrator to set your area.')
        return redirect('election_detail', election_id=election_id)
    else:
        try:
            election = LegacyElection.objects.get(id=election_id)
        except LegacyElection.DoesNotExist:
            messages.error(request, 'This election does not exist.')
            return redirect('election_list')
        if check_election_status(election) == 'Ongoing':
            if not LegacyVote.objects.filter(election=election, user=request.user).exists():
                colour_settings = ColourSettings.objects.filter(user=request.user).first()
                if request.method == 'POST':
                    form = VoteForm(request.POST, area=request.user.legacyprofile.area)
                    if form.is_valid():
                        vote = form.save(commit=False)
                        vote.election = election
                        vote.user = request.user
                        vote.save()
                        messages.success(request, 'Vote has been submitted!')
                        return redirect('election_detail', election_id=election_id)
                else:
                    form = VoteForm(area=request.user.legacyprofile.area)
                return render(request, 'apps/vote/vote.html', {
                    'colour_settings': colour_settings,
                    'form': form,
                    'election': election
                })
            else:
                messages.error(request, 'You have already voted in this election.')
                return redirect('election_detail', election_id=election_id)
        elif check_election_status(election) == 'Upcoming':
            messages.error(request, 'This election has not started yet.')
            return redirect('election_detail', election_id=election_id)
        else:
            messages.error(request, 'This election has ended.')
            return redirect('election_detail', election_id=election_id)


@login_required
def vote_history(request, election_id):
    if request.user.is_staff or request.user.is_superuser:
        try:
            election = LegacyElection.objects.get(id=election_id)
        except LegacyElection.DoesNotExist:
            messages.error(request, 'This election does not exist.')
            return redirect('election_list')
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        election_vote_history = LegacyVote.objects.filter(election=election)
        return render(request, 'apps/vote/vote_history.html', {
            'colour_settings': colour_settings,
            'vote_history': election_vote_history,
            'election': election
        })
    else:
        messages.error(request, 'You are not authorised to access this page.')
        return redirect('homepage')


def election_result(request, election_id):
    try:
        election = LegacyElection.objects.get(id=election_id)
    except LegacyElection.DoesNotExist:
        messages.error(request, 'This election does not exist.')
        return redirect('election_list')
    if check_election_status(election) != 'Finished' and (request.user.is_staff or request.user.is_superuser) or check_election_status(election) == 'Finished':
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
    try:
        election = LegacyElection.objects.get(id=election_id)
    except LegacyElection.DoesNotExist:
        messages.error(request, 'This election does not exist.')
        return redirect('election_list')
    if check_election_status(election) != 'Finished' and (request.user.is_staff or request.user.is_superuser) or check_election_status(election) == 'Finished':
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
    all_party_old = LegacyParty.objects.all()
    all_party_new = NewParty.objects.all()
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/party/party_list.html', {
            'colour_settings': colour_settings,
            'party_list_old': all_party_old,
            'party_list_new': all_party_new
        })
    else:
        return render(request, 'apps/party/party_list.html', {
            'party_list_old': all_party_old,
            'party_list_new': all_party_new
        })


@login_required
def add_party(request):
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
    if request.user.is_staff or request.user.is_superuser:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        utility_log = UtilityMissionLog.objects.all()
        return render(request, 'apps/utils/utils.html', {
            'colour_settings': colour_settings,
            'import_legacy_data': len(UtilityMissionLog.objects.filter(field='import_legacy_data',done=True)) > 0,
            'utility_log': utility_log
        })
    else:
        messages.error(request, 'You are not authorised to access this page.')
        return redirect('homepage')


@login_required()
def import_legacy_data(request):
    if request.user.is_staff or request.user.is_superuser:
        try:
            users.seed.seed_data()
            messages.success(request, 'Legacy data has been imported!')
            UtilityMissionLog.objects.create(
                user=request.user,
                field = 'import_legacy_data',
                done = True,
                description = 'Import legacy data successfully.'
            )
            return redirect('utils')
        except Exception as e:
            messages.error(request, 'Legacy data import failed : ' + str(e))
            users.models.UtilityMissionLog.objects.create(
                user=request.user,
                field = 'import_legacy_data',
                done = False,
                description = 'Import legacy data failed : ' + str(e)
            )
            return redirect('utils')
    else:
        messages.error(request, 'You are not authorised to access this function.')
        return redirect('homepage')
