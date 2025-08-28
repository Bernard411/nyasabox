from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_song, name='upload_song'),
    path('profile/', views.artist_profile, name='artist_profile'),
    path('download/<int:song_id>/', views.download_song, name='download_song'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]