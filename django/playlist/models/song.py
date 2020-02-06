import os
import subprocess
from mutagen.mp3 import MP3

from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.conf import settings

from config.models import Station

from playlist.models.album import (
    Album,
    UserAlbumOnStation,
    AlbumOnStationQuerySet,
    UserAlbumRating,
    UserAlbumFave,
    AlbumOnStation,
)
from playlist.base_classes import (
    ObjectWithCooldown,
    ObjectWithVoteStats,
    ObjectOnStation,
    ObjectWithCooldownManager,
    ObjectOnStationQuerySet,
    ObjectWithCooldownQuerySet,
)
from playlist.models.artist import Artist
from playlist.models.group import Group
from playlist.exceptions import ScanMetadataException

from utils.sql_model_mapper import SQLModelMapper
from utils.parse_string_to_number import parse_string_to_number
from utils import filetools
from utils.make_searchable_string import make_searchable_string

_mp3gain_path = filetools.which("mp3gain")


def set_umask():
    os.setpgrp()
    os.umask(0o02)


class SongToArtist(models.Model):
    song = models.ForeignKey("Song", on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    position = models.SmallIntegerField(default=0)

    class Meta:
        unique_together = (("artist", "song"),)

    def to_json(self):
        return {
            "name": self.artist.name,
            "order": self.position,
        }


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
    scanned = models.BooleanField(default=False)

    # ID3 Tags / Song Data
    disc_number = models.SmallIntegerField(blank=True, null=True)
    length = models.SmallIntegerField()
    link_text = models.TextField(blank=True, null=True)
    replaygain = models.TextField(blank=True, null=True)
    name = models.TextField()
    name_searchable = models.TextField()
    track_number = models.SmallIntegerField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    year = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @staticmethod
    def parse_tag(filename, mp3_file, id3, required=False):
        tags = mp3_file.tags.getall(id3)
        tag = None
        if len(tags) > 0 and len(str(tags[0])) > 0:
            tag = str(tags[0]).strip()
        if not tag and required:
            raise ScanMetadataException(f"Song {filename} has no {id3} tag.")
        return tag

    @staticmethod
    def get_replaygain(mp3_file):
        replaygain_tag = None
        for xxx_tag in mp3_file.tags.getall("TXXX"):
            if xxx_tag.desc.lower() == "replaygain_track_gain":
                replaygain_tag = str(xxx_tag)
        return replaygain_tag

    @classmethod
    def scan(cls, filename, origin_station, stations):
        mp3_file = MP3(filename, translate=False)

        if not mp3_file.tags:
            cls.objects.filter(filename=filename).update(enabled=False)
            raise ScanMetadataException('Song filename "%s" has no tags.' % filename)

        name = cls.parse_tag(filename, mp3_file, "TIT2", required=True)
        album_tag = cls.parse_tag(filename, mp3_file, "TALB", required=True)
        artists_tag = cls.parse_tag(filename, mp3_file, "TPE1", required=True)

        song = cls.objects_with_disabled.filter(
            Q(filename__iexact=filename)
            | Q(name__iexact=name, album__name__iexact=album_tag)
        ).update_or_create(
            filename=filename,
            name=name,
            name_searchable=make_searchable_string(name),
            scanned=True,
            origin_station=origin_station,
            file_mtime=os.stat(filename)[8],
        )[
            0
        ]

        song.track_number = parse_string_to_number(
            cls.parse_tag(filename, mp3_file, "TRCK")
        )
        song.disc_number = parse_string_to_number(
            cls.parse_tag(filename, mp3_file, "TPOS")
        )
        song.link_text = cls.parse_tag(filename, mp3_file, "COMM")
        song.url = cls.parse_tag(filename, mp3_file, "WXXX")
        song.year = parse_string_to_number(
            cls.parse_tag(filename, mp3_file, "TYER")
            or cls.parse_tag(filename, mp3_file, "TDRC")
        )
        song.replaygain = cls.get_replaygain(mp3_file)
        song.length = int(mp3_file.info.length)

        if not song.replaygain and settings.RW_SCANNER_MP3GAIN:
            gain_std, gain_error = subprocess.Popen(
                [_mp3gain_path, "-o", "-q", "-s", "i", "-p", "-k", "-T", filename],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=set_umask,
            ).communicate()
            if len(gain_error) > 0:
                raise ScanMetadataException(
                    'Error when replay gaining "%s": %s' % (filename, gain_error)
                )
            mp3_file = MP3(filename, translate=False)
            song.replaygain = cls.get_replaygain(mp3_file)

        song.save()

        song.songonstation_set.filter(station__in=stations).update(enabled=True)
        song.songonstation_set.exclude(station__in=stations).update(enabled=False)

        # Associate these after saving
        song.album = Album.objects.get_or_create(
            name__iexact=album_tag, defaults={"name": album_tag}
        )[0]
        song.album.determine_enabled()

        song_to_artists = set()
        for index, artist_tag in enumerate(artists_tag):
            artist_tag = artist_tag.strip()
            artist = Artist.objects.get_or_create(
                name__iexact=artist_tag, defaults={"name": artist_tag}
            )[0]
            song_to_artist = SongToArtist.objects.update_or_create(
                artist=artist, defaults={"artist": artist, "position": index}
            )[0]
            song_to_artists.add(song_to_artist)
        song.songtoartist_set.set(song_to_artists)

        song_to_groups = set()
        groups_to_check = set(
            stg.group for stg in song.songtogroup_set.select_related("group").all()
        )
        for genre_tag in cls.parse_tag(filename, mp3_file, "TCON").split(","):
            genre_tag = genre_tag.strip()
            group = Group.objects.get_or_create(
                name__iexact=genre_tag, defaults={"name": genre_tag}
            )[0]
            groups_to_check.add(group)
            song_to_groups.add(
                SongToGroup.objects.update_or_create(
                    group=group, defaults={"group": group, "is_tag": True}
                )[0]
            )
        for song_to_group in song.songtogroup_set.filter(is_tag=False):
            song_to_groups.add(song_to_group)
        song.songtogroup_set.set(song_to_groups)
        for group in groups_to_check:
            group.determine_enabled()

        song.artist_json = [stg.to_json() for stg in song_to_artists]
        song.save()


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
