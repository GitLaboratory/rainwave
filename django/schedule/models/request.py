from django.db import models

from users.models import User
from playlist.models import Song


class RequestLinePosition(models.Model):
    user = models.OneToOneField(User, models.CASCADE, primary_key=True)
    station_id = models.SmallIntegerField(db_column="sid")
    wait_start = models.IntegerField(blank=True, null=True, db_column="line_wait_start")
    expiry_tune_in = models.IntegerField(
        blank=True, null=True, db_column="line_expiry_tune_in"
    )
    expiry_election = models.IntegerField(
        blank=True, null=True, db_column="line_expiry_election"
    )
    has_had_valid_song = models.BooleanField(
        blank=True, null=True, db_column="line_has_had_valid"
    )

    class Meta:
        managed = False
        db_table = "r4_request_line"


class Request(models.Model):
    id = models.AutoField(primary_key=True, db_column="reqstor_id")
    order = models.SmallIntegerField(blank=True, null=True, db_column="reqstor_order")
    user = models.ForeignKey(User, models.CASCADE, db_column="user_id")
    song = models.ForeignKey(Song, models.CASCADE, db_column="song_id")
    station_id = models.SmallIntegerField(db_column="sid")

    class Meta:
        managed = False
        db_table = "r4_request_store"
        ordering = ["order", "id"]


class FulfilledRequest(models.Model):
    request_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.CASCADE)
    song = models.ForeignKey(Song, models.CASCADE)
    fulfilled_at = models.IntegerField(
        blank=True, null=True, db_column="request_fulfilled_at"
    )
    wait_time = models.IntegerField(
        blank=True, null=True, db_column="request_wait_time"
    )
    line_size = models.IntegerField(
        blank=True, null=True, db_column="request_line_size"
    )
    count_at_time = models.IntegerField(
        blank=True, null=True, db_column="request_at_count"
    )
    sid = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_request_history"
