from django.contrib import admin
from .models import Artist, Song


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("user", "bio", "created_at")
    search_fields = ("user__username", "bio")
    list_filter = ("created_at",)


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "genre", "uploaded_at", "download_count")
    search_fields = ("title", "artist__user__username", "genre")
    list_filter = ("genre", "uploaded_at")
    readonly_fields = ("download_count",)  # prevent manual tampering in admin
