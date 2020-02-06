from django.db import models
from django.contrib.auth import get_user_model

from config.models import Station
from playlist.models import (
    SongOnStation,
    SongOnStationQuerySet,
    UserSongAlbumOnStation,
    UserSongRating,
    UserSongFave,
    Song,
    AlbumOnStation,
    Album,
    UserAlbumRating,
    UserAlbumFave,
)

from utils.sql_model_mapper import SQLModelMapper


class RequestLinePosition(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, unique=True, db_index=True
    )
    station = models.ForeignKey(Station, on_delete=models.CASCADE, db_index=True)
    wait_start = models.IntegerField(blank=True, null=True)
    expires_if_not_tuned_in_at = models.DateTimeField(blank=True, null=True)
    expires_if_no_valid_song_at = models.DateTimeField(blank=True, null=True)
    has_had_valid_song = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]


class RequestQuerySet(models.QuerySet):
    def user_song_album_iterator(self, user, sort_sql="position, id"):
        return UserRequestSongAlbumOnStation.iterate(
            *SongOnStationQuerySet.get_user_song_album_left_joined_query(
                query=self.select_related("song_on_station__song__album").query,
                user=user,
                sort_sql=sort_sql,
            )
        )


class Request(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    song_on_station = models.ForeignKey(SongOnStation, on_delete=models.CASCADE)
    position = models.SmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]


class UserRequestSongAlbumOnStation(SQLModelMapper):
    request: Request = None
    user_rating: UserSongRating = None
    user_fave: UserSongFave = None
    song_on_station: SongOnStation = None
    song: Song = None
    album_on_station: AlbumOnStation = None
    album: Album = None
    user_rating: UserAlbumRating = None
    user_fave: UserAlbumFave = None

    _models = ((Request, "request"),) + UserSongAlbumOnStation._models


class FulfilledRequest(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    song_on_station = models.ForeignKey(SongOnStation, on_delete=models.CASCADE)
    fulfilled_at = models.DateTimeField(auto_now_add=True)
    wait_time_for_fulfillment = models.IntegerField()
    line_size_at_fulfillment = models.IntegerField()

    class Meta:
        ordering = ["id"]
