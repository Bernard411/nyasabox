from django import forms
from .models import Song, Artist
from django.contrib.auth.models import User

class SongUploadForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'genre', 'audio_file', 'cover_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'genre': forms.TextInput(attrs={'class': 'form-control'}),
            'audio_file': forms.FileInput(attrs={'class': 'form-control'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ArtistProfileForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['bio']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class ZipUploadForm(forms.Form):
    zip_file = forms.FileField(
        label='Upload ZIP file containing MP3s',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.zip'})
    )