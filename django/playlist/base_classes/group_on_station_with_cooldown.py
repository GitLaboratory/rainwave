from django.db import models

from .object_on_station import ObjectOnStation, ObjectOnStationQuerySet
from .object_with_cooldown import ObjectWithCooldown, ObjectWithCooldownQuerySet


class GroupOnStationWithCooldownQuerySet(
    ObjectOnStationQuerySet, ObjectWithCooldownQuerySet
):
    pass


class UnfilteredGroupOnStationWithCooldownManager(models.Manager):
    pass


class GroupOnStationWithCooldownManager(UnfilteredGroupOnStationWithCooldownManager):
    def get_queryset(self):
        return super().get_queryset().filter(enabled=True)


class GroupOnStationWithCooldown(ObjectOnStation, ObjectWithCooldown):
    objects = GroupOnStationWithCooldownManager.from_queryset(
        GroupOnStationWithCooldownQuerySet
    )()
    objects_with_disabled = UnfilteredGroupOnStationWithCooldownManager.from_queryset(
        GroupOnStationWithCooldownQuerySet
    )()

    class Meta:
        abstract = True
