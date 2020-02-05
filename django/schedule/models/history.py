from django.db import models

from playlist.models import SongOnStation


class PlayedSong(models.Model):
    when = models.DateTimeField(auto_now_add=True)
    song_on_station = models.ForeignKey(SongOnStation, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-id"]
