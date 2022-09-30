from django import forms

from apps.models import Area, Candidate


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
    area = forms.ModelChoiceField(label="Area", queryset=Area.objects.all(), widget=forms.Select(
        attrs={'class': 'form-control'}),
        help_text="The area that the candidate is running for.")

    class Meta:
        model = Candidate
        fields = ['name', 'image', 'description', 'area']
