from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, FileResponse
from .models import Song, Artist
from .forms import SongUploadForm, ArtistProfileForm, ZipUploadForm
from django.contrib import messages
import os
from zipfile import ZipFile
import eyed3
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from PIL import Image
import io
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, FileResponse
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, FileResponse
from .models import Song, Artist
from .forms import SongUploadForm, ArtistProfileForm, ZipUploadForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login, logout


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def home(request):
    songs = Song.objects.all().order_by('-uploaded_at')
    return render(request, 'home.html', {'songs': songs})

def song_detail(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    share_url = request.build_absolute_uri()
    return render(request, 'song_detail.html', {'song': song, 'share_url': share_url})

@login_required
def upload_album(request):
    if not hasattr(request.user, 'artist'):
        Artist.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = AlbumUploadForm(request.POST, request.FILES)
        if form.is_valid():
            album = form.save(commit=False)
            album.artist = request.user.artist
            album.save()
            messages.success(request, 'Album created successfully!')
            return redirect('upload_song')  # Redirect to song upload to add tracks
    else:
        form = AlbumUploadForm()
    return render(request, 'upload_album.html', {'form': form})

@login_required
def upload_song(request):
    if not hasattr(request.user, 'artist'):
        Artist.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = SongUploadForm(request.POST, request.FILES, artist=request.user.artist)
        if form.is_valid():
            song = form.save(commit=False)
            song.artist = request.user.artist
            
            # If it's part of an album, handle track numbers
            if song.album:
                # Check if track number is provided, if not assign next available
                if not song.track_number:
                    last_track = Song.objects.filter(album=song.album).order_by('-track_number').first()
                    song.track_number = last_track.track_number + 1 if last_track else 1
                # Ensure track number is unique for this album
                while Song.objects.filter(album=song.album, track_number=song.track_number).exists():
                    song.track_number += 1
            
            song.save()
            messages.success(request, 'Song uploaded successfully!')
            
            # Option to add another song to the same album
            if song.album:
                return redirect('add_to_album', album_id=song.album.id)
            return redirect('home')
    else:
        form = SongUploadForm(artist=request.user.artist)
    return render(request, 'upload_song.html', {'form': form})

@login_required
def add_to_album(request, album_id):
    album = get_object_or_404(Album, id=album_id, artist=request.user.artist)
    
    if request.method == 'POST':
        form = SongUploadForm(request.POST, request.FILES, artist=request.user.artist)
        if form.is_valid():
            song = form.save(commit=False)
            song.artist = request.user.artist
            song.album = album
            
            # Handle track number
            if not song.track_number:
                last_track = Song.objects.filter(album=album).order_by('-track_number').first()
                song.track_number = last_track.track_number + 1 if last_track else 1
            
            # Ensure track number is unique
            while Song.objects.filter(album=album, track_number=song.track_number).exists():
                song.track_number += 1
                
            song.save()
            messages.success(request, 'Song added to album successfully!')
            
            # Option to add another song
            if 'add_another' in request.POST:
                return redirect('add_to_album', album_id=album.id)
            return redirect('album_detail', album_id=album.id)
    else:
        # Pre-fill the album field
        form = SongUploadForm(artist=request.user.artist, initial={'album': album})
    
    return render(request, 'add_to_album.html', {
        'form': form,
        'album': album
    })

def album_detail(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    songs = album.songs.all().order_by('track_number')
    
    return render(request, 'album_detail.html', {
        'album': album,
        'songs': songs
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def upload_zip(request):
    if request.method == 'POST':
        form = ZipUploadForm(request.POST, request.FILES)
        if form.is_valid():
            zip_file = request.FILES['zip_file']
            fs = FileSystemStorage()
            zip_filename = fs.save(zip_file.name, zip_file)
            zip_path = fs.path(zip_filename)

            try:
                with ZipFile(zip_path, 'r') as zip_ref:
                    for file_name in zip_ref.namelist():
                        if file_name.lower().endswith('.mp3'):
                            with zip_ref.open(file_name) as mp3_file:
                                mp3_content = mp3_file.read()
                                mp3_temp_path = fs.save(f'temp/{file_name}', mp3_content)
                                mp3_full_path = fs.path(mp3_temp_path)

                                audio = eyed3.load(mp3_full_path)
                                if audio is None or audio.tag is None:
                                    logger.warning(f"No metadata found for {file_name}")
                                    fs.delete(mp3_temp_path)
                                    continue

                                title = audio.tag.title or file_name.rsplit('.', 1)[0]
                                artist_name = audio.tag.artist or 'Unknown Artist'
                                genre = audio.tag.genre.name if audio.tag.genre else 'Unknown'
                                
                                user, created = User.objects.get_or_create(
                                    username=artist_name.replace(' ', '_').lower(),
                                    defaults={'username': artist_name.replace(' ', '_').lower()}
                                )
                                if created:
                                    user.set_unusable_password()
                                    user.save()
                                artist, _ = Artist.objects.get_or_create(user=user)

                                mp3_file_obj = File(open(mp3_full_path, 'rb'), name=file_name)
                                song = Song(
                                    artist=artist,
                                    title=title,
                                    genre=genre,
                                    audio_file=mp3_file_obj
                                )

                                if audio.tag.images:
                                    for image in audio.tag.images:
                                        if image.mime_type.startswith('image/'):
                                            img_data = image.image_data
                                            img = Image.open(io.BytesIO(img_data))
                                            img_format = img.format.lower() if img.format else 'jpeg'
                                            cover_filename = f"covers/{title}_{artist_name}.{img_format}"
                                            cover_path = fs.path(cover_filename)
                                            img.save(cover_path, format=img_format)
                                            song.cover_image = File(open(cover_path, 'rb'), name=cover_filename)
                                            break

                                song.save()
                                fs.delete(mp3_temp_path)
                                if song.cover_image:
                                    fs.delete(cover_path)

                messages.success(request, 'ZIP file processed successfully!')
                fs.delete(zip_path)
                return redirect('home')
            except Exception as e:
                logger.error(f"Error processing ZIP: {str(e)}")
                messages.error(request, f"Error processing ZIP file: {str(e)}")
                fs.delete(zip_path)
    else:
        form = ZipUploadForm()
    return render(request, 'upload_zip.html', {'form': form})

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
        response = FileResponse(file, content_type='audio/mpeg')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response

def stream_song(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    file_path = song.audio_file.path
    with open(file_path, 'rb') as file:
        response = FileResponse(file, content_type='audio/mpeg')
        response['Content-Disposition'] = 'inline'
        return response

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