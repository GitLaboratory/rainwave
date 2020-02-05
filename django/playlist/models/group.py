from django.db import models

from playlist.base_classes import ObjectOnStation, GroupBlocksElections


class Group(models.Model):
    name = models.CharField(max_length=1024)
    name_searchable = models.CharField(max_length=1024)

    class Meta:
        ordering = ["name"]


class GroupOnStation(ObjectOnStation, GroupBlocksElections):
    group = models.ForeignKey(Group, models.CASCADE)
    visible = models.BooleanField(default=True)
