from django.db import models

from users.models import User
from playlist.models import Song

from schedule.models.schedule_sequence import next_schedule_sequence_id


class Event(models.Model):
    id = models.IntegerField(
        default=next_schedule_sequence_id, primary_key=True, db_column="sched_id"
    )
    station_id = models.SmallIntegerField(db_column="sid")

    end = models.IntegerField(blank=True, null=True, db_column="sched_end")
    end_actual = models.IntegerField(
        blank=True, null=True, db_column="sched_end_actual"
    )
    event_type = models.TextField(blank=True, null=True, db_column="sched_type")
    in_progress = models.BooleanField(
        default=False, blank=True, null=True, db_column="sched_in_progress"
    )
    name = models.TextField(blank=True, null=True, db_column="sched_name")
    public = models.BooleanField(
        default=True, blank=True, null=True, db_column="sched_public"
    )
    start = models.IntegerField(blank=True, null=True, db_column="sched_start")
    start_actual = models.IntegerField(
        blank=True, null=True, db_column="sched_start_actual"
    )
    timed = models.BooleanField(
        default=True, blank=True, null=True, db_column="sched_timed"
    )
    url = models.TextField(blank=True, null=True, db_column="sched_url")
    use_crossfade = models.BooleanField(
        default=True, blank=True, null=True, db_column="sched_use_crossfade"
    )
    use_tag_suffix = models.BooleanField(
        default=True, blank=True, null=True, db_column="sched_use_tag_suffix"
    )
    used = models.BooleanField(
        default=False, blank=True, null=True, db_column="sched_used"
    )

    dj = models.ForeignKey(
        User, models.SET_NULL, blank=True, null=True, db_column="sched_dj_user"
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column="sched_creator_user_id",
    )

    class Meta:
        managed = False
        db_table = "r4_schedule"
        ordering = ["id"]


class SongInEvent(models.Model):
    id = models.IntegerField(
        default=next_schedule_sequence_id, primary_key=True, db_column="one_up_id"
    )
    event = models.ForeignKey(Event, models.CASCADE, db_column="sched_id")
    song = models.ForeignKey(Song, models.CASCADE, db_column="song_id")
    order = models.SmallIntegerField(blank=True, null=True, db_index="one_up_order")
    used = models.BooleanField(
        default=False, blank=True, null=True, db_index="one_up_used"
    )
    queued = models.BooleanField(
        default=False, blank=True, null=True, db_index="one_up_queued"
    )
    station_id = models.SmallIntegerField(db_index="one_up_sid")

    class Meta:
        managed = False
        db_table = "r4_one_ups"
