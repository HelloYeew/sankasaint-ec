from django import forms

from apps.models import Area


class AddAreaForm(forms.ModelForm):
    name = forms.CharField(label="Area Name", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Area Name'}),
        help_text="The name of the area.")
    description = forms.CharField(label="Area Description", widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Area Description'}),
        help_text="Short description of the area.")

    class Meta:
        model = Area
        fields = ['name', 'description']
