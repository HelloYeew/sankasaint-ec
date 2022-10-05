from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views

from apps.models import Vote
from users.forms import UserCreationForms, UserSettingsForm, ProfileForm
from users.models import ColourSettings, Profile


class LogoutAndRedirect(auth_views.LogoutView):
    # Redirect to / after logout
    def get_next_page(self):
        messages.success(self.request, 'You have been logged out.')
        return '/'


def signup(request):
    if request.method == 'POST':
        form = UserCreationForms(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}! Now you can login.')
            return redirect('login')
    else:
        form = UserCreationForms()
    return render(request, 'users/signup.html', {'form': form})


def settings(request):
    colour_settings = ColourSettings.objects.filter(user=request.user).first()
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=colour_settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings saved successfully!')
            return redirect('settings')
    else:
        form = UserSettingsForm(instance=colour_settings)
    return render(request, 'users/settings.html', {
        'colour_settings': colour_settings,
        'form': form
    })


def profile(request, user_id):
    try:
        user = Profile.objects.get(id=user_id)
    except Profile.DoesNotExist:
        messages.error(request, 'This user does not exist.')
        return redirect('homepage')
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        votes = Vote.objects.filter(user__id=user_id)
        return render(request, 'users/profile.html', {
            'colour_settings': colour_settings,
            'profile': user,
            'vote_history': votes
        })
    else:
        return render(request, 'users/profile.html', {
            'profile': user
        })


@login_required
def edit_profile(request):
    user = Profile.objects.get(user=request.user)
    colour_settings = ColourSettings.objects.filter(user=request.user).first()
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile', user_id=request.user.id)
    else:
        form = ProfileForm(instance=user)
    return render(request, 'users/edit_profile.html', {
        'form': form,
        'colour_settings': colour_settings
    })
