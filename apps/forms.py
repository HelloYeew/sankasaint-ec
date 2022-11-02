from django import forms
from django.contrib.auth.models import User

from apps.models import LegacyArea, LegacyCandidate, LegacyElection, LegacyVote, LegacyParty, NewArea, NewCandidate, \
    NewElection


class AreaForm(forms.ModelForm):
    name = forms.CharField(label="Area Name", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Area Name'}),
        help_text="The name of the area.")
    description = forms.CharField(label="Area Description", widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Area Description'}),
        help_text="Short description of the area.")

    class Meta:
        model = NewArea
        fields = ['name', 'description']


class CandidateForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all().order_by('id'), label="Citizen", widget=forms.Select(
        attrs={'class': 'form-control'}), help_text="The citizen that will be the candidate.")
    image = forms.ImageField(label="Candidate Image", required=False, widget=forms.FileInput(
        attrs={'class': 'form-control-file', 'placeholder': 'Candidate Image'}),
        help_text="The image of the candidate. This is not required but better if you have one.")
    description = forms.CharField(label="Candidate Description", widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Candidate Description'}),
        help_text="Short description of the candidate.")
    area = forms.ModelChoiceField(label="Area", queryset=NewArea.objects.all().order_by('id'), widget=forms.Select(
        attrs={'class': 'form-control'}),
                                  help_text="The area that the candidate is running for.")

    class Meta:
        model = NewCandidate
        fields = ['user', 'image', 'description', 'area']


class StartElectionForm(forms.ModelForm):
    name = forms.CharField(label="Election Name", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Election Name'}),
        help_text="The name of the election.")
    front_image = forms.ImageField(label="Election Image", widget=forms.FileInput(
        attrs={'class': 'form-control-file', 'placeholder': 'Election Front Image'}),
        help_text="The image showing at the front of the election.")
    description = forms.CharField(label="Election Description", widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Election Description'}),
        help_text="Short description of the election.")
    start_date = forms.DateTimeField(label="Start Date", widget=forms.DateTimeInput(
        attrs={'class': 'form-control', 'placeholder': 'Start Date'}), required=False,
        help_text="The start time of the election. Fill nothing if you want to start the election immediately. ("
                  "Format : YYYY-MM-DD HH:MM:SS e.g. 2022-10-03 00:19:46)")
    end_date = forms.DateTimeField(label="End Date", widget=forms.DateTimeInput(
        attrs={'class': 'form-control', 'placeholder': 'End Date'}),
        help_text="The end time of the election. (Format : YYYY-MM-DD HH:MM:SS e.g. 2022-10-03 00:19:46)")

    class Meta:
        model = NewElection
        fields = ['name', 'front_image', 'description', 'start_date', 'end_date']


class EditElectionForm(forms.ModelForm):
    front_image = forms.ImageField(label="Election Image", widget=forms.FileInput(
        attrs={'class': 'form-control-file', 'placeholder': 'Election Front Image'}),
        help_text="The image showing at the front of the election.")
    description = forms.CharField(label="Election Description", widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Election Description'}),
        help_text="Short description of the election.")

    class Meta:
        model = NewElection
        fields = ['front_image', 'description']


class VoteForm(forms.ModelForm):
    candidate = forms.ModelChoiceField(label="Candidate", queryset=LegacyCandidate.objects.all(), widget=forms.Select(
        attrs={'class': 'form-control'}),
                                       help_text="The candidate that you want to vote for.")

    def __init__(self, *args, **kwargs):
        area = kwargs.pop('area')
        super(VoteForm, self).__init__(*args, **kwargs)
        self.fields['candidate'].queryset = LegacyCandidate.objects.filter(area=area)

    class Meta:
        model = LegacyVote
        fields = ['candidate']


class PartyForm(forms.ModelForm):
    name = forms.CharField(label="Party Name", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Party Name'}),
        help_text="The name of the party.")
    image = forms.ImageField(label="Party Image", required=False, widget=forms.FileInput(
        attrs={'class': 'form-control-file', 'placeholder': 'Party Image'}),
        help_text="The image of the party. This is not required but better if you have one.")
    description = forms.CharField(label="Party Description", widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Party Description'}),
        help_text="Short description of the party.")
    # TODO: Re-enable this after investigation on error on initialize the database
    # candidates = forms.ModelMultipleChoiceField(label="Candidates", queryset=Candidate.objects.all(),
    #     widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': Candidate.objects.all().count(), 'placeholder': 'Candidates'}),
    #     help_text='The candidates that are in the party. Hold down “Control”, or “Command” on a Mac, to select more than one.')

    class Meta:
        model = LegacyParty
        fields = ['name', 'image', 'description']
