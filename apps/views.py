from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from apps.forms import AddAreaForm
from apps.models import Area
from users.models import ColourSettings


@login_required
def homepage(request):
    colour_settings = ColourSettings.objects.filter(user=request.user).first()
    return render(request, 'homepage.html', {
        'colour_settings': colour_settings
    })


def area_list(request):
    colour_settings = ColourSettings.objects.filter(user=request.user).first()
    all_area = Area.objects.all()
    return render(request, 'apps/area/area_list.html', {
        'colour_settings': colour_settings,
        'all_area': all_area
    })


@login_required
def add_area(request):
    if request.user.is_staff or request.user.is_superuser:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        if request.method == 'POST':
            form = AddAreaForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Area has been added!')
                return redirect('area_list')
        else:
            form = AddAreaForm()
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
            form = AddAreaForm(request.POST, instance=area)
            if form.is_valid():
                form.save()
                messages.success(request, 'Edit area successfully!')
                return redirect('area_list')
        else:
            form = AddAreaForm(instance=area)
        return render(request, 'apps/area/edit_area.html', {
            'colour_settings': colour_settings,
            'form': form,
            'area': area
        })
    else:
        messages.error(request, 'You are not authorised to access this page.')
        return redirect('homepage')


def area_detail(request, area_id):
    colour_settings = ColourSettings.objects.filter(user=request.user).first()
    area = Area.objects.get(id=area_id)
    return render(request, 'apps/area/area_detail.html', {
        'colour_settings': colour_settings,
        'area': area
    })
