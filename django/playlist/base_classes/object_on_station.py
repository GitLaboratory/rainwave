from django.db import models

from misc.models import Station


class ObjectOnStationQuerySet(models.QuerySet):
    pass


class UnfilteredObjectOnStationManager(models.Manager):
    pass


class ObjectOnStationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(enabled=True)


class ObjectOnStation(models.Model):
    objects = ObjectOnStationManager.from_queryset(ObjectOnStationQuerySet)
    objects_with_disabled = ObjectOnStationManager.from_queryset(
        ObjectOnStationQuerySet
    )

    enabled = models.BooleanField(default=True, db_index=True)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)

    class Meta:
        abstract = True
