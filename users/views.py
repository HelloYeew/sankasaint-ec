from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views

from apps.models import Vote
from users.forms import UserCreationForms, UserSettingsForm
from users.models import ColourSettings, Profile


class LogoutAndRedirect(auth_views.LogoutView):
    # Redirect to / after logout
    def get_next_page(self):
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
    if request.user.is_authenticated:
        user = Profile.objects.get(id=user_id)
        colour_settings = ColourSettings.objects.filter(user=request.user).first()
        votes = Vote.objects.filter(user__id=user_id)
        return render(request, 'users/profile.html', {
            'colour_settings': colour_settings,
            'profile': user,
            'vote_history': votes
        })
    else:
        user = Profile.objects.get(id=user_id)
        return render(request, 'users/profile.html', {
            'profile': user
        })
