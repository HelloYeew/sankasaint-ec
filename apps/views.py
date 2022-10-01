from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from apps.forms import AreaForm, CandidateForm
from apps.models import Area, Candidate
from users.models import ColourSettings


def homepage(request):
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'homepage.html', {
            'colour_settings': colour_settings
        })
    else:
        return render(request, 'homepage.html')


def area_list(request):
    all_area = Area.objects.all()
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/area/area_list.html', {
            'colour_settings': colour_settings,
            'all_area': all_area
        })
    else:
        return render(request, 'apps/area/area_list.html', {
            'all_area': all_area
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
        area = Area.objects.get(id=area_id)
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


def area_detail(request, area_id):
    area = Area.objects.get(id=area_id)
    available_candidate = Candidate.objects.filter(area=area)
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/area/area_detail.html', {
            'colour_settings': colour_settings,
            'area': area,
            'available_candidate': available_candidate
        })
    else:
        return render(request, 'apps/area/area_detail.html', {
            'area': area,
            'available_candidate': available_candidate
        })


def candidate_list(request):
    all_candidate = Candidate.objects.all()
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/candidate/candidate_list.html', {
            'colour_settings': colour_settings,
            'all_candidate': all_candidate
        })
    else:
        return render(request, 'apps/candidate/candidate_list.html', {
            'all_candidate': all_candidate
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
        candidate = Candidate.objects.get(id=candidate_id)
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


def candidate_detail(request, candidate_id):
    candidate = Candidate.objects.get(id=candidate_id)
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        return render(request, 'apps/candidate/candidate_detail.html', {
            'colour_settings': colour_settings,
            'candidate': candidate
        })
    else:
        return render(request, 'apps/candidate/candidate_detail.html', {
            'candidate': candidate
        })
