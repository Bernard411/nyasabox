from django import forms
from .models import Song, Artist

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