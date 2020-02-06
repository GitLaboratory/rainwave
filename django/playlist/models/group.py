from django.db import models

from playlist.base_classes import ObjectOnStation, GroupBlocksElections


class Group(models.Model):
    name = models.CharField(max_length=1024)
    name_searchable = models.CharField(max_length=1024)

    class Meta:
        ordering = ["name"]

    def determine_enabled(self):
        for group_on_station in self.grouponstation_set.all():
            group_on_station.determined_enabled()


class GroupOnStation(ObjectOnStation, GroupBlocksElections):
    group = models.ForeignKey(Group, models.CASCADE)
    visible = models.BooleanField(default=True)

    @property
    def songs(self):
        return self.group.songtogroup_set.filter(
            song__songonstation__station_id=self.station_id,
        )

    def determine_enabled(self):
        enabled = self.songs.exists()
        if enabled != self.enabled:
            self.enabled = enabled
            self.save()
