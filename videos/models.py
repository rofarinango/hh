from django.db import models

class Playlist(models.Model):
    playlist_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    season_number = models.IntegerField()

    def __str__(self):
        return self.title

class Episode(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='episodes')
    title = models.CharField(max_length=255)
    video_id = models.CharField(max_length=255, unique=True)
    thumbnail = models.URLField()
    duration = models.IntegerField()

    def __str__(self):
        return self.title