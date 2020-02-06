from django.db import models

from django.contrib.auth import get_user_model
from playlist.base_classes import (
    GroupOnStationWithCooldown,
    GroupOnStationWithCooldownQuerySet,
    UnfilteredGroupOnStationWithCooldownManager,
    GroupOnStationWithCooldownManager,
    GroupBlocksElections,
)

from config.models import Station

from utils.sql_model_mapper import SQLModelMapper


class Album(models.Model):
    added_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=1024)
    name_searchable = models.CharField(max_length=1024)
    year = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def determine_enabled(self):
        for album_on_station in self.albumonstation_set.all():
            album_on_station.determine_enabled()


class UserAlbumFave(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    fave = models.BooleanField(default=False)

    class Meta:
        index_together = [("album", "user")]


class UserAlbumRating(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)

    complete = models.BooleanField(default=False)
    rating = models.FloatField()

    class Meta:
        index_together = [("album", "user", "station"), ("album", "station")]


class AlbumOnStationQuerySet(GroupOnStationWithCooldownQuerySet):
    rainwave_join_query = (
        f'   LEFT JOIN "{UserAlbumRating._meta.db_table}" ON ('
        f'       original_query."__core_album_id" = "{UserAlbumRating._meta.db_table}".album_id '
        f'       AND original_query."__core_sid" = "{UserAlbumRating._meta.db_table}".station_id '
        f'       AND "{UserAlbumRating._meta.db_table}".user_id = %(user_id)s '
        f"   ) "
        f'   LEFT JOIN "{UserAlbumFave._meta.db_table}" ON ( '
        f'       original_query."__core_album_id" = "{UserAlbumFave._meta.db_table}".album_id '
        f'       AND "{UserAlbumFave._meta.db_table}".user_id = %(user_id)s '
        f"   ) "
    )
    rainwave_join_query_select = (
        f'"{Album._meta.db_table}".album_id AS "__core_album_id"'
    )

    def user_album_iterator(self, user=None):
        query = str(self.query).replace(
            "SELECT ",
            f'SELECT {self.rainwave_join_query_select}, "{AlbumOnStation._meta.db_table}"".sid AS "__core_sid", ',
            1,
        )
        return UserAlbumOnStation.iterate(
            f"WITH original_query AS ({query}) "
            "SELECT "
            "   * "
            "FROM "
            "   original_query " + self.rainwave_join_query + "ORDER BY name ",
            {"user_id": user.id if isinstance(user, get_user_model()) else user},
        )


class UnfilteredAlbumOnStationManager(UnfilteredGroupOnStationWithCooldownManager):
    def get_queryset(self):
        return super().get_queryset().select_related("album")


class AlbumOnStationManager(GroupOnStationWithCooldownManager):
    def get_queryset(self):
        return super().get_queryset().select_related("album").filter(exists=True)


class AlbumOnStation(GroupOnStationWithCooldown, GroupBlocksElections):
    album = models.ForeignKey(Album, models.CASCADE)

    rating = models.FloatField(default=0, db_index=True)
    rating_count = models.IntegerField(default=0, db_index=True)
    request_count = models.IntegerField(default=0,)
    requests_pending = models.BooleanField(default=False, db_index=True)

    fave_count = models.IntegerField(default=0)
    newest_song_added_on = models.DateTimeField(auto_now_add=True)

    objects = AlbumOnStationManager.from_queryset(AlbumOnStationQuerySet)()
    objects_with_deleted = UnfilteredAlbumOnStationManager.from_queryset(
        AlbumOnStationQuerySet
    )()

    class Meta:
        unique_together = (("album", "station"),)
        index_together = (("album", "station"), ("enabled", "station"))

    def get_art_url(self):
        pass

    @property
    def songs(self):
        return self.album.song_set.filter(station=self.station)

    def determine_enabled(self):
        enabled = self.songs.exists()
        if enabled != self.enabled:
            self.enabled = enabled
            self.save()


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
