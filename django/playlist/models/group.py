from django.db import models

from playlist.base_classes.base_song_group import BaseSongGroup


class Group(BaseSongGroup):
    id = models.AutoField(primary_key=True, db_column="group_id")

    cool_time = models.SmallIntegerField(
        blank=True, null=True, db_column="group_cool_time"
    )
    elec_block = models.SmallIntegerField(
        blank=True, null=True, db_column="group_elec_block"
    )
    name = models.TextField(blank=True, null=True, db_column="group_name")
    name_searchable = models.TextField(db_column="group_name_searchable")

    class Meta:
        managed = False
        db_table = "r4_groups"


class GroupOnStation(models.Model):
    group = models.ForeignKey(Group, models.CASCADE, blank=True, null=True)

    station_id = models.SmallIntegerField(db_column="sid")
    display = models.BooleanField(default=False, blank=True, null=True, db_index=True)

    class Meta:
        managed = False
        db_table = "r4_group_sid"
