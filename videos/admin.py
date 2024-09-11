from django.contrib import admin
from .models import Playlist, Episode
@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['title']

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ['title']