from django.db import models

from playlist.models import Song

from utils.time import now


class PlayedSong(models.Model):
    id = models.AutoField(primary_key=True, db_column="songhist_id")
    time = models.IntegerField(
        default=now, blank=True, null=True, db_column="songhist_time"
    )
    station_id = models.SmallIntegerField(db_column="sid")
    song = models.ForeignKey(Song, models.CASCADE)

    class Meta:
        managed = False
        db_table = "r4_song_history"
        ordering = ["-id"]
