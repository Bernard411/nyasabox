from .models import Song
import json

def songs_json(request):
    songs = Song.objects.all().order_by('-uploaded_at')
    songs_data = [
        {
            'id': song.id,
            'title': song.title,
            'artist': song.artist.user.username,
            'genre': song.genre,
            'url': request.build_absolute_uri(song.audio_file.url),
            'cover_image': request.build_absolute_uri(song.cover_image.url) if song.cover_image else ''
        } for song in songs
    ]
    return {'songs_json': json.dumps(songs_data)}