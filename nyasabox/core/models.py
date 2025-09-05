from django.db import models
from django.contrib.auth.models import User

class Artist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Album(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='albums')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='album_covers/', blank=True, null=True)
    release_date = models.DateField(auto_now_add=True)
    is_ep = models.BooleanField(default=False)  # EP if True, Album if False
    
    def __str__(self):
        return f"{self.title} by {self.artist.user.username}"

# Update the Song model to include album relationship
class Song(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='songs')
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True, related_name='songs')
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=50)
    audio_file = models.FileField(upload_to='songs/')
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    download_count = models.PositiveIntegerField(default=0)
    track_number = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.title} by {self.artist.user.username}"