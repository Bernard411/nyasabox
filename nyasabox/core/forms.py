from django import forms
from .models import *
from django.contrib.auth.models import User

class AlbumUploadForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'description', 'cover_image', 'is_ep']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_ep': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class SongUploadForm(forms.ModelForm):
    album = forms.ModelChoiceField(
        queryset=Album.objects.none(),  # Will be set in the view
        required=False,
        empty_label="Single (No Album)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    track_number = forms.IntegerField(
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Song
        fields = ['title', 'genre', 'audio_file', 'cover_image', 'album', 'track_number']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'genre': forms.TextInput(attrs={'class': 'form-control'}),
            'audio_file': forms.FileInput(attrs={'class': 'form-control'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.artist = kwargs.pop('artist', None)
        super(SongUploadForm, self).__init__(*args, **kwargs)
        if self.artist:
            self.fields['album'].queryset = Album.objects.filter(artist=self.artist)

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