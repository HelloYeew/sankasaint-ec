from django import forms

from apps.models import Area, Candidate, Election, Vote


class AreaForm(forms.ModelForm):
    name = forms.CharField(label="Area Name", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Area Name'}),
        help_text="The name of the area.")
    description = forms.CharField(label="Area Description", widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Area Description'}),
        help_text="Short description of the area.")

    class Meta:
        model = Area
        fields = ['name', 'description']


class CandidateForm(forms.ModelForm):
    name = forms.CharField(label="Candidate Name", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Candidate Name'}),
        help_text="The name of the candidate.")
    image = forms.ImageField(label="Candidate Image", required=False, widget=forms.FileInput(
        attrs={'class': 'form-control-file', 'placeholder': 'Candidate Image'}),
        help_text="The image of the candidate. This is not required but better if you have one.")
    description = forms.CharField(label="Candidate Description", widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Candidate Description'}),
        help_text="Short description of the candidate.")
    area = forms.ModelChoiceField(label="Area", queryset=Area.objects.all().order_by('id'), widget=forms.Select(
        attrs={'class': 'form-control'}),
        help_text="The area that the candidate is running for.")

    class Meta:
        model = Candidate
        fields = ['name', 'image', 'description', 'area']


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
        model = Election
        fields = ['name', 'front_image', 'description', 'start_date', 'end_date']


class EditElectionForm(forms.ModelForm):
    front_image = forms.ImageField(label="Election Image", widget=forms.FileInput(
        attrs={'class': 'form-control-file', 'placeholder': 'Election Front Image'}),
        help_text="The image showing at the front of the election.")
    description = forms.CharField(label="Election Description", widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Election Description'}),
        help_text="Short description of the election.")

    class Meta:
        model = Election
        fields = ['front_image', 'description']


class VoteForm(forms.ModelForm):
    candidate = forms.ModelChoiceField(label="Candidate", queryset=Candidate.objects.all(), widget=forms.Select(
        attrs={'class': 'form-control'}),
        help_text="The candidate that you want to vote for.")

    def __init__(self, *args, **kwargs):
        area = kwargs.pop('area')
        super(VoteForm, self).__init__(*args, **kwargs)
        self.fields['candidate'].queryset = Candidate.objects.filter(area=area)

    class Meta:
        model = Vote
        fields = ['candidate']
