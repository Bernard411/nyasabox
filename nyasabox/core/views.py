from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Song, Artist
from .forms import SongUploadForm, ArtistProfileForm
from django.contrib import messages
import os

def home(request):
    songs = Song.objects.all().order_by('-uploaded_at')
    return render(request, 'home.html', {'songs': songs})

@login_required
def upload_song(request):
    if not hasattr(request.user, 'artist'):
        Artist.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = SongUploadForm(request.POST, request.FILES)
        if form.is_valid():
            song = form.save(commit=False)
            song.artist = request.user.artist
            song.save()
            messages.success(request, 'Song uploaded successfully!')
            return redirect('home')
    else:
        form = SongUploadForm()
    return render(request, 'upload_song.html', {'form': form})

@login_required
def artist_profile(request):
    artist, created = Artist.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ArtistProfileForm(request.POST, instance=artist)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('artist_profile')
    else:
        form = ArtistProfileForm(instance=artist)
    return render(request, 'artist_profile.html', {'form': form, 'artist': artist})

def download_song(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    song.download_count += 1
    song.save()
    
    file_path = song.audio_file.path
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='audio/mpeg')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response
    
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')