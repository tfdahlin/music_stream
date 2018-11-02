from django.db import models
from django.contrib.auth import get_user_model

class Artist (models.Model):
    name = models.CharField(max_length=1000, null=True)

class Album (models.Model):
    name = models.CharField(max_length=200, null=True)

class Playlist (models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    public = models.BooleanField(default=False)

class Song (models.Model):
    name = models.CharField(max_length=1000)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, blank = True, null=True)
    filepath = models.CharField(max_length=1000)
    track_length = models.CharField(max_length=100)
    playlists = models.ManyToManyField(Playlist)

