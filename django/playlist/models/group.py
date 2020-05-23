from django.db import models

from playlist.base_classes import ObjectOnStation, GroupBlocksElections


class Group(models.Model):
    name = models.CharField(max_length=1024)
    name_searchable = models.CharField(max_length=1024)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_stations_group_should_exist_on(self):
        return set(
            self.songtogroup_set.filter(
                song__songonstation__station_id__isnull=False
            ).values_list("song__songonstation__station_id", flat=True)
        )

    def determine_enabled(self):
        should_exist_on = self.get_stations_group_should_exist_on()
        self.grouponstation_set.exclude(station_id__in=should_exist_on).update(
            enabled=False
        )
        for station_id in should_exist_on:
            GroupOnStation.objects_with_disabled.update_or_create(
                group=self,
                station_id=station_id,
                defaults={"group": self, "station_id": station_id, "enabled": True,},
            )


class GroupOnStation(ObjectOnStation, GroupBlocksElections):
    group = models.ForeignKey(Group, models.CASCADE)
    visible = models.BooleanField(default=True, db_index=True)

    @property
    def song_set(self):
        return self.group.songtogroup_set.filter(
            song__songonstation__station_id=self.station_id,
        )

    def determine_enabled(self):
        enabled = self.station_id in self.group.get_stations_group_should_exist_on()
        if enabled != self.enabled:
            self.enabled = enabled
            self.save()
