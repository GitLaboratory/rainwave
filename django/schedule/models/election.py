from django.db import models

from users.models import User
from playlist.models import Song, SongOnStation
from schedule.models.event import Event

from utils.schedule_sequence import next_schedule_sequence_id
from utils.election_entry_types import ElectionEntryTypes


class ElectionEntry(models.Model):
    id = models.AutoField(primary_key=True, db_column="entry_id")
    song = models.ForeignKey(Song, models.CASCADE, db_column="song_id")
    election = models.ForeignKey("Election", models.CASCADE, db_column="elec_id")
    entry_type = models.SmallIntegerField(
        default=ElectionEntryTypes.NORMAL, blank=True, null=True,
    )
    position = models.SmallIntegerField(
        blank=True, null=True, db_column="entry_position"
    )
    votes = models.SmallIntegerField(
        default=0, blank=True, null=True, db_column="entry_votes"
    )

    class Meta:
        managed = False
        db_table = "r4_election_entries"
        ordering = ["entry_position"]

    _song_on_station = None

    @property
    def song_on_station(self):
        if self._song_on_station:
            self._song_on_station = SongOnStation.objects.get(
                song=self.song, station_id=self.election.station_id
            )
        return self._song_on_station

    @song_on_station.setter
    def song_on_station(self, new_song_on_station):
        self.song = new_song_on_station.song


class Election(models.Model):
    id = models.IntegerField(
        default=next_schedule_sequence_id,
        primary_key=True,
        db_column="elec_id",
        db_index=True,
    )
    station_id = models.SmallIntegerField(db_column="sid", db_index=True)
    event = models.ForeignKey(Event, models.CASCADE, blank=True, null=True)
    entries = models.ManyToManyField(Song, through=ElectionEntry)

    used = models.BooleanField(
        default=False, blank=True, null=True, db_column="elec_used", db_index=True
    )

    in_progress = models.BooleanField(
        default=False, blank=True, null=True, db_column="elec_in_progress"
    )
    start_actual = models.IntegerField(
        blank=True, null=True, db_column="elec_start_actual"
    )
    election_type = models.TextField(blank=True, null=True, db_column="elec_type")
    priority = models.BooleanField(
        default=False, blank=True, null=True, db_column="elec_priority"
    )

    class Meta:
        managed = False
        db_table = "r4_elections"
        ordering = ["id"]


class Vote(models.Model):
    user = models.ForeignKey(User, models.CASCADE, db_column="user_id")
    song = models.ForeignKey(Song, models.CASCADE, db_column="song_id")
    election = models.ForeignKey(
        Election, models.SET_NULL, blank=True, null=True, db_column="elec_id"
    )
    entry = models.ForeignKey(
        ElectionEntry, models.SET_NULL, blank=True, null=True, db_column="entry_id"
    )

    id = models.AutoField(primary_key=True, db_column="vote_id")
    time = models.IntegerField(blank=True, null=True, db_column="vote_time")
    rank_at_time = models.IntegerField(blank=True, null=True, db_column="vote_at_rank")
    vote_count_at_time = models.IntegerField(
        blank=True, null=True, db_column="vote_at_count"
    )
    station_id = models.SmallIntegerField(blank=True, null=True, db_column="station_id")

    class Meta:
        managed = False
        db_table = "r4_vote_history"
