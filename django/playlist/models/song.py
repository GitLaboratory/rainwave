from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField

from playlist.models.album import (
    Album,
    UserAlbumOnStation,
    AlbumOnStationQuerySet,
    UserAlbumRating,
    UserAlbumFave,
    AlbumOnStation,
)
from playlist.models.artist import Artist
from playlist.models.group import Group
from misc.models import Station

from playlist.base_classes import (
    ObjectWithCooldown,
    ObjectWithVoteStats,
    ObjectOnStation,
    ObjectWithCooldownManager,
    ObjectOnStationQuerySet,
    ObjectWithCooldownQuerySet,
)


from utils.sql_model_mapper import SQLModelMapper


class SongToArtist(models.Model):
    song = models.ForeignKey("Song", on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    order = models.SmallIntegerField(default=0)
    is_tag = models.BooleanField(default=True)

    class Meta:
        unique_together = (("artist", "song"),)


class SongToGroup(models.Model):
    song = models.ForeignKey("Song", on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    is_tag = models.BooleanField(default=True)

    class Meta:
        unique_together = (("group", "song"),)


class SongManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(enabled=True)


class Song(ObjectWithCooldown, ObjectWithVoteStats):
    objects = SongManager.from_queryset(models.QuerySet)()
    objects_with_disabled = models.Manager.from_queryset(models.QuerySet)()

    enabled = models.BooleanField(default=True, db_index=True)
    origin_station = models.ForeignKey(
        Station, blank=True, null=True, on_delete=models.SET_NULL
    )

    # Related Metadata
    album = models.ForeignKey(Album, models.CASCADE)
    artists = models.ManyToManyField(Artist, through=SongToArtist)
    groups = models.ManyToManyField(Group, through=SongToGroup)

    # Rainwave data
    added_on = models.DateTimeField(auto_now_add=True)
    artist_json = JSONField(default=list)
    fave_count = models.IntegerField(default=0)
    file_mtime = models.IntegerField()
    filename = models.TextField()
    rating = models.FloatField(blank=True, null=True, db_index=True)
    rating_count = models.IntegerField(default=0, db_index=True)
    request_count = models.IntegerField(default=0)
    request_only = models.BooleanField(default=False, db_index=False)
    scanned = models.BooleanField(default=True)

    # ID3 Tags / Song Data
    disc_number = models.SmallIntegerField(blank=True, null=True)
    length = models.SmallIntegerField()
    link_text = models.TextField(blank=True, null=True)
    replay_gain = models.TextField(blank=True, null=True)
    name = models.TextField()
    name_searchable = models.TextField()
    track_number = models.SmallIntegerField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    year = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class SongOnStationQuerySet(ObjectOnStationQuerySet, ObjectWithCooldownQuerySet):
    @classmethod
    def _get_left_joined_query(
        cls, query, user, sort_sql, extra_selects="", extra_joins=""
    ):
        query = str(query).replace(
            "SELECT ",
            (
                "SELECT "
                f'  "{SongOnStation._meta.db_table}".song_id AS "__core_song_id", '
                f'  "{SongOnStation._meta.db_table}".sid AS "__core_sid", '
                f"   {extra_selects} "
            ),
            count=1,
        )
        return (
            f"WITH original_query AS ({query}) "
            "SELECT "
            "   * "
            "FROM "
            f"   original_query {extra_joins} "
            f'   LEFT JOIN "{UserSongRating._meta.db_table}" ON ('
            f'      original_query."__core_song_id" = "{UserSongRating._meta.db_table}".song_id '
            f'       AND "{UserSongRating._meta.db_table}".user_id = %(user_id)s '
            "    ) "
            f"   LEFT JOIN {UserSongFave._meta.db_table} ON ("
            f'       original_query."__core_song_id" = "{UserSongFave._meta.db_table}".song_id '
            f'       AND "{UserSongFave._meta.db_table}".user_id = %(user_id)s '
            "    ) "
            f"ORDER BY {sort_sql} ",
            {"user_id": user.id if isinstance(user, get_user_model()) else user},
        )

    @classmethod
    def get_user_song_album_left_joined_query(cls, query, user, sort_sql):
        return cls._get_left_joined_query(
            query=query,
            user=user,
            sort_sql=sort_sql,
            extra_selects=f"{AlbumOnStationQuerySet.rainwave_join_query_select}, ",
            extra_joins=AlbumOnStationQuerySet.rainwave_join_query,
        )

    def user_song_iterator(self, user=None, sort_sql="song_title"):
        return UserSongOnStation.iterate(
            *self.__class__._get_left_joined_query(self.query, user, sort_sql)
        )

    def user_song_album_iterator(self, user=None, sort_sql="song_title"):
        return UserSongAlbumOnStation.iterate(
            *self.__class__.get_user_song_album_left_joined_query(
                query=self.select_related("song__album").query,
                user=user,
                sort_sql=sort_sql,
            )
        )


class UnfilteredSongOnStationManager(ObjectWithCooldownManager):
    def get_queryset(self):
        return super().get_queryset().select_related("song")


class SongOnStationManager(UnfilteredSongOnStationManager):
    def get_queryset(self):
        return super().get_queryset().filter(exists=True, song__enabled=True)


class SongOnStation(ObjectOnStation, ObjectWithCooldown):
    objects = SongOnStationManager.from_queryset(SongOnStationQuerySet)()
    objects_with_deleted = UnfilteredSongOnStationManager.from_queryset(
        SongOnStationQuerySet
    )()

    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    electable = models.BooleanField(default=True, db_index=True)
    electable_blocked_by = models.CharField(max_length=64, blank=True, null=True)
    electable_blocked_for = models.SmallIntegerField(default=0)

    class Meta:
        unique_together = (("song", "station"),)
        index_together = (("song", "station"),)


class UserSongRating(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    rating = models.FloatField()
    when = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("user", "song"),)
        index_together = (("user", "song"),)


class UserSongFave(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    fave = models.BooleanField()

    class Meta:
        unique_together = (("user", "song"),)
        index_together = (("user", "song"),)


class UserSongOnStation(SQLModelMapper):
    user_rating: UserSongRating = None
    user_fave: UserSongFave = None
    song_on_station: SongOnStation = None
    song: Song = None

    _models = (
        (UserSongRating, "user_rating"),
        (UserSongFave, "user_fave"),
        (SongOnStation, "song_on_station"),
        (Song, "song"),
    )


class UserSongAlbumOnStation(SQLModelMapper):
    user_rating: UserSongRating = None
    user_fave: UserSongFave = None
    song_on_station: SongOnStation = None
    song: Song = None
    album_on_station: AlbumOnStation = None
    album: Album = None
    user_rating: UserAlbumRating = None
    user_fave: UserAlbumFave = None

    _models = UserSongOnStation._models + UserAlbumOnStation._models
