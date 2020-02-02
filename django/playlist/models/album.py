from django.db import models

from users.models import User
from playlist.base_classes.base_song_group import BaseSongGroup

from playlist.utils.sql_model_mapper import SQLModelMapper
from utils.time import now


class Album(BaseSongGroup):
    id = models.AutoField(primary_key=True, db_column="album_id")

    added_on = models.IntegerField(
        default=now, blank=True, null=True, db_column="album_added_on"
    )
    name = models.TextField(blank=True, null=True, db_column="album_name")
    name_searchable = models.TextField(db_column="album_name_searchable")
    year = models.SmallIntegerField(blank=True, null=True, db_column="album_year")

    class Meta:
        managed = False
        db_table = "r4_albums"
        ordering = ["name"]


class UserAlbumFave(models.Model):
    album = models.ForeignKey(Album, models.CASCADE)
    user = models.ForeignKey(User, models.CASCADE)

    fave = models.BooleanField(blank=True, null=True, db_column="album_fave")

    class Meta:
        managed = False
        db_table = "r4_album_faves"
        index_together = [("album", "user")]


class UserAlbumRating(models.Model):
    album = models.ForeignKey(Album, models.CASCADE, db_index=False)
    user = models.ForeignKey(User, models.CASCADE, db_index=False)

    complete = models.BooleanField(
        blank=True, null=True, db_column="album_rating_complete"
    )
    rating = models.FloatField(blank=True, null=True, db_column="album_rating_user")
    station_id = models.SmallIntegerField(db_column="sid")

    class Meta:
        managed = False
        db_table = "r4_album_ratings"
        index_together = [("album", "user", "station_id"), ("album_id", "station_id")]


class AlbumOnStationQuerySet(models.QuerySet):
    rainwave_join_query = (
        "   LEFT JOIN r4_album_ratings ON ("
        '       original_query."__core_album_id" = r4_album_ratings.album_id '
        '       AND original_query."__core_sid" = r4_album_ratings.sid '
        "       AND r4_album_ratings.user_id = %(user_id)s "
        "   ) "
        "   LEFT JOIN r4_album_faves ON ( "
        '       original_query."__core_album_id" = r4_album_faves.album_id '
        "       AND r4_album_faves.user_id = %(user_id)s "
        "   ) "
    )
    rainwave_join_query_select = 'r4_albums.album_id AS "__core_album_id"'

    def user_album_iterator(self, user=None):
        query = str(self.query).replace(
            "SELECT ",
            f'SELECT {self.rainwave_join_query_select}, r4_album_sid.sid AS "__core_sid", ',
            1,
        )
        return UserAlbumOnStation.iterate(
            f"WITH original_query AS ({query}) "
            "SELECT "
            "   * "
            "FROM "
            "   original_query "
            "ORDER BY album_name ",
            {"user_id": user.id if isinstance(user, User) else user},
        )


class UnfilteredAlbumOnStationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("album")


class AlbumOnStationManager(UnfilteredAlbumOnStationManager):
    def get_queryset(self):
        return super().get_queryset().filter(exists=True)


class AlbumOnStation(models.Model):
    id = models.IntegerField(db_column="album_sid_id", primary_key=True, db_index=True)
    album = models.ForeignKey(Album, models.CASCADE)
    station_id = models.SmallIntegerField(db_column="sid", db_index=True)

    exists = models.BooleanField(
        default=True, blank=True, null=True, db_column="album_exists", db_index=True
    )
    rating = models.FloatField(default=0, db_column="album_rating", db_index=True)
    rating_count = models.IntegerField(
        default=0, blank=True, null=True, db_column="album_rating_count", db_index=True
    )
    request_count = models.IntegerField(
        default=0, blank=True, null=True, db_column="album_request_count"
    )
    requests_pending = models.BooleanField(
        default=False,
        blank=True,
        null=True,
        db_column="album_requests_pending",
        db_index=True,
    )

    cool = models.BooleanField(
        default=False, blank=True, null=True, db_column="album_cool",
    )
    cool_lowest = models.IntegerField(
        default=0, blank=True, null=True, db_column="album_cool_lowest",
    )
    cool_multiply = models.FloatField(
        default=1, blank=True, null=True, db_column="album_cool_multiply"
    )
    cool_override = models.IntegerField(
        blank=True, null=True, db_column="album_cool_override"
    )
    elec_last = models.IntegerField(
        default=0, blank=True, null=True, db_column="album_elec_last",
    )
    fave_count = models.IntegerField(
        default=0, blank=True, null=True, db_column="album_fave_count"
    )
    newest_song_time = models.IntegerField(
        default=0, blank=True, null=True, db_column="album_newest_song_time"
    )
    played_last = models.IntegerField(
        default=0, blank=True, null=True, db_column="album_played_last",
    )
    song_count = models.SmallIntegerField(
        default=0, blank=True, null=True, db_column="album_song_count"
    )
    updated = models.IntegerField(
        default=0, blank=True, null=True, db_column="album_updated"
    )
    vote_count = models.IntegerField(
        default=0, blank=True, null=True, db_column="album_vote_count"
    )
    vote_share = models.FloatField(
        blank=True, default=True, db_column="album_vote_share"
    )
    votes_seen = models.IntegerField(default=0, db_column="album_votes_seen")

    objects = AlbumOnStationManager.from_queryset(AlbumOnStationQuerySet)()
    objects_with_deleted = UnfilteredAlbumOnStationManager.from_queryset(
        AlbumOnStationQuerySet
    )()

    class Meta:
        managed = False
        db_table = "r4_album_sid"
        unique_together = (("album", "station_id"),)
        index_together = (("album", "station_id"), ("exists", "station_id"))


class UserAlbumOnStation(SQLModelMapper):
    album_on_station: AlbumOnStation = None
    album: Album = None
    user_rating: UserAlbumRating = None
    user_fave: UserAlbumFave = None

    _models = (
        (AlbumOnStation, "album_on_station"),
        (Album, "album"),
        (UserAlbumRating, "user_rating"),
        (UserAlbumFave, "user_fave"),
    )
