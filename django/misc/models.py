from django.db import models

from users.models import User

from utils.time import now


class Donations(models.Model):
    id = models.AutoField(primary_key=True, db_column="donation_id")
    user = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL, db_column="user_id"
    )

    amount = models.FloatField(blank=True, null=True, db_column="donation_amount")
    message = models.TextField(blank=True, null=True, db_column="donation_message")
    private = models.BooleanField(blank=True, null=True, db_column="donation_private")

    class Meta:
        managed = False
        db_table = "r4_donations"
        ordering = ["-id"]


class ListenerCount(models.Model):
    station_id = models.SmallIntegerField(db_column="sid", db_index=True)
    guests = models.SmallIntegerField(blank=True, null=True, db_column="lc_guests")
    guests_active = models.SmallIntegerField(
        blank=True, null=True, db_column="lc_guests_active"
    )
    time = models.IntegerField(
        default=now, blank=True, null=True, db_column="lc_time", db_index=True
    )
    users = models.SmallIntegerField(blank=True, null=True, db_column="lc_users")
    users_active = models.SmallIntegerField(
        blank=True, null=True, db_column="lc_users_active"
    )

    class Meta:
        managed = False
        db_table = "r4_listener_counts"
        ordering = ["-time"]
