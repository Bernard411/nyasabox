from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_song, name='upload_song'),
    path('upload-zip/', views.upload_zip, name='upload_zip'),
    path('profile/', views.artist_profile, name='artist_profile'),
    path('download/<int:song_id>/', views.download_song, name='download_song'),
    path('stream/<int:song_id>/', views.stream_song, name='stream_song'),
    path('song/<int:song_id>/', views.song_detail, name='song_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]