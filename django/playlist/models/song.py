from django.db import models

from users.models import User
from playlist.models.album import Album
from playlist.models.artist import Artist
from playlist.models.group import Group

from utils.time import now


class SongToArtist(models.Model):
    song = models.ForeignKey("Song", models.CASCADE)
    artist = models.OneToOneField(Artist, models.CASCADE)
    order = models.SmallIntegerField(
        default=0, blank=True, null=True, db_column="artist_order"
    )
    is_tag = models.BooleanField(
        default=True, blank=True, null=True, db_column="artist_is_tag"
    )

    class Meta:
        managed = False
        db_table = "r4_song_artist"
        unique_together = (("artist", "song"),)


class SongToGroup(models.Model):
    song = models.ForeignKey("Song", models.CASCADE)
    group = models.OneToOneField(Group, models.CASCADE)
    is_tag = models.BooleanField(
        default=True, blank=True, null=True, db_column="group_is_tag"
    )

    class Meta:
        managed = False
        db_table = "r4_song_group"
        unique_together = (("group", "song"),)


class Song(models.Model):
    id = models.AutoField(primary_key=True, db_column="song_id")
    album = models.ForeignKey(Album, models.CASCADE)
    artists = models.ManyToManyField(Artist, through=SongToArtist)
    groups = models.ManyToManyField(Group, through=SongToGroup)

    rating = models.FloatField(default=0, db_column="song_rating", db_index=True)
    rating_count = models.IntegerField(
        default=0, db_column="song_rating_count", db_index=True
    )
    verified = models.BooleanField(
        default=True, db_column="song_verified", db_index=True
    )

    added_on = models.IntegerField(default=now, db_column="song_added_on")
    artist_parseable = models.TextField(db_column="song_artist_parseable")
    artist_tag = models.TextField(db_column="song_artist_tag")
    cool_multiply = models.FloatField(default=1, db_column="song_cool_multiply")
    cool_override = models.IntegerField(
        blank=True, null=True, db_column="song_cool_override"
    )
    disc_number = models.SmallIntegerField(
        blank=True, null=True, db_column="song_disc_number"
    )
    fave_count = models.IntegerField(default=0, db_column="song_fave_count")
    file_mtime = models.IntegerField(db_column="song_file_mtime")
    filename = models.TextField(db_column="song_filename")
    length = models.SmallIntegerField(db_column="song_length")
    link_text = models.TextField(blank=True, null=True, db_column="song_link_text")
    origin_sid = models.SmallIntegerField(db_column="song_origin_sid")
    replay_gain = models.TextField(blank=True, null=True, db_column="song_replay_gain")
    request_count = models.IntegerField(default=0, db_column="song_request_count")
    scanned = models.BooleanField(default=True, db_column="song_scanned")
    title = models.TextField(db_column="song_title")
    title_searchable = models.TextField(db_column="song_title_searchable")
    track_number = models.SmallIntegerField(
        blank=True, null=True, db_column="song_track_number"
    )
    url = models.TextField(blank=True, null=True, db_column="song_url")
    vote_count = models.IntegerField(default=0, db_column="song_vote_count")
    vote_share = models.FloatField(blank=True, null=True, db_column="song_vote_share")
    votes_seen = models.IntegerField(default=0, db_column="song_votes_seen")
    year = models.SmallIntegerField(blank=True, null=True, db_column="song_year")

    class Meta:
        managed = False
        db_table = "r4_songs"


class SongOnStation(models.Model):
    song = models.ForeignKey(Song, models.CASCADE)

    station_id = models.SmallIntegerField(db_column="sid", db_index=True)
    cool = models.BooleanField(
        default=False, blank=True, null=True, db_column="song_cool", db_index=True
    )
    elec_blocked = models.BooleanField(
        default=False,
        blank=True,
        null=True,
        db_column="song_elec_blocked",
        db_index=True,
    )
    exists = models.BooleanField(
        default=True, blank=True, null=True, db_column="song_exists", db_index=True
    )
    request_only = models.BooleanField(
        default=False,
        blank=True,
        null=True,
        db_column="song_request_only",
        db_index=True,
    )

    cool_end = models.IntegerField(
        default=0, blank=True, null=True, db_column="song_cool_end"
    )
    elec_appearances = models.IntegerField(
        default=0, blank=True, null=True, db_column="song_elec_appearances"
    )
    elec_blocked_by = models.TextField(
        blank=True, null=True, db_column="song_elec_blocked_by"
    )
    elec_blocked_num = models.SmallIntegerField(
        default=0, blank=True, null=True, db_column="song_elec_blocked_num"
    )
    elec_last = models.IntegerField(
        default=0, blank=True, null=True, db_column="song_elec_last"
    )
    played_last = models.IntegerField(
        blank=True, null=True, db_column="song_played_last"
    )
    request_only_end = models.IntegerField(
        default=0, blank=True, null=True, db_column="song_request_only_end"
    )

    class Meta:
        managed = False
        db_table = "r4_song_sid"
        unique_together = (("song", "station_id"),)


class SongRating(models.Model):
    song = models.ForeignKey(Song, models.CASCADE)
    user = models.ForeignKey(User, models.CASCADE)
    rating_user = models.FloatField(blank=True, null=True, db_column="song_rating_user")
    rated_at = models.IntegerField(blank=True, null=True, db_column="song_rated_at")
    rated_at_rank = models.IntegerField(
        blank=True, null=True, db_column="song_rated_at_rank"
    )
    rated_at_count = models.IntegerField(
        blank=True, null=True, db_column="song_rated_at_count"
    )
    fave = models.BooleanField(
        blank=True, null=True, db_column="song_fave", db_index=True
    )

    class Meta:
        managed = False
        db_table = "r4_song_ratings"
        unique_together = (("user", "song"),)
        index_together = (("user", "song"),)
