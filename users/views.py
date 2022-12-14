from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from apps.models import LegacyVote, VoteCheck
from users.forms import UserCreationForms, UserSettingsForm, ProfileForm
from users.models import ColourSettings, NewProfile


class LogoutAndRedirect(auth_views.LogoutView):
    """
    A view that logs a user out and redirects to the homepage.
    """
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
    """
    An ayaka's settings page.
    """
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


@login_required
def profile(request):
    """
    Show a user's profile.
    """
    user_object = User.objects.filter(id=request.user.id).first()
    try:
        user = NewProfile.objects.get(id=request.user.id)
    except NewProfile.DoesNotExist:
        messages.error(request, 'This user does not exist.')
        return redirect('homepage')
    if request.user.is_authenticated:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        votes_legacy = LegacyVote.objects.filter(user__id=request.user.id).order_by('id')
        votes_new = VoteCheck.objects.filter(user__id=request.user.id).order_by('id')
        return render(request, 'users/profile.html', {
            'colour_settings': colour_settings,
            'profile': user,
            'user': user_object,
            'vote_history': votes_new,
            'vote_history_legacy': votes_legacy
        })
    else:
        return render(request, 'users/profile.html', {
            'profile': user
        })


@login_required
def profile_with_id(request, user_id):
    """
    Show a user's profile.
    """
    user_object = User.objects.filter(id=user_id).first()
    try:
        user = NewProfile.objects.get(id=user_id)
    except NewProfile.DoesNotExist:
        messages.error(request, 'This user does not exist.')
        return redirect('homepage')
    if request.user.is_superuser or request.user.is_staff:
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        votes_legacy = LegacyVote.objects.filter(user__id=user_id).order_by('id')
        votes_new = VoteCheck.objects.filter(user__id=user_id).order_by('id')
        return render(request, 'users/profile.html', {
            'colour_settings': colour_settings,
            'profile': user,
            'user': user_object,
            'vote_history': votes_new,
            'vote_history_legacy': votes_legacy
        })
    else:
        return redirect('profile')


@login_required
def edit_profile(request):
    """
    Edit current logged in user's profile.
    """
    user = NewProfile.objects.get(user=request.user)
    colour_settings = ColourSettings.objects.filter(user=request.user).first()
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'users/edit_profile.html', {
        'form': form,
        'colour_settings': colour_settings
    })


@login_required
def create_user_utility(request):
    """
    A utility to create a new user like signup.

    This menu can be only accessed by staff and superuser for some testing purposes.
    """
    colour_settings = ColourSettings.objects.filter(user=request.user).first()
    if request.user.is_superuser or request.user.is_staff:
        if request.method == 'POST':
            form = UserCreationForms(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, f'Account created successfully for {username}! Now you can login.')
                return redirect('utils')
        else:
            form = UserCreationForms()
        return render(request, 'apps/utils/create_user.html', {'form': form, 'colour_settings': colour_settings})
    else:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('homepage')
