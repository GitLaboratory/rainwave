from django.db import models

from users.models.user import User


class Listener(models.Model):
    id = models.AutoField(primary_key=True, db_column="listener_id")
    user = models.ForeignKey(
        User, models.CASCADE, blank=True, null=True, default=1, db_column="user_id"
    )

    station_id = models.SmallIntegerField(db_column="sid", db_index=True)

    agent = models.TextField(blank=True, null=True, db_column="listener_agent")
    icecast_id = models.IntegerField(db_column="listener_icecast_id")
    ip = models.TextField(blank=True, null=True, db_column="listener_ip")
    key = models.TextField(blank=True, null=True, db_column="listener_key")
    lock = models.BooleanField(blank=True, null=True, db_column="listener_lock")
    lock_counter = models.SmallIntegerField(
        default=0, blank=True, null=True, db_column="listener_lock_counter"
    )
    lock_sid = models.SmallIntegerField(
        blank=True, null=True, db_column="listener_lock_sid"
    )
    purge = models.BooleanField(
        default=False, blank=True, null=True, db_column="listener_purge"
    )
    relay = models.TextField(blank=True, null=True, db_column="listener_relay")
    voted_entry = models.IntegerField(
        blank=True, null=True, db_column="listener_voted_entry"
    )

    class Meta:
        managed = False
        db_table = "r4_listeners"
