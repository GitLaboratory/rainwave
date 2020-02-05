from django.db import models


class ObjectWithCooldownQuerySet(models.QuerySet):
    def is_available(self):
        return super().filter(is_on_cooldown=False, is_request_only=False)

    def is_on_cooldown(self):
        return super().filter(is_on_cooldown=True)

    def is_available_for_request(self):
        return super().filter(is_on_cooldown=False, is_request_only=True)


class BaseObjectWithCooldownManager(models.Manager):
    pass


ObjectWithCooldownManager = BaseObjectWithCooldownManager.from_queryset(
    ObjectWithCooldownQuerySet
)


class ObjectWithCooldown(models.Model):
    objects = ObjectWithCooldownManager()

    is_on_cooldown = models.BooleanField(default=False, db_index=True)
    cooldown_ends_at = models.DateTimeField(auto_now_add=True)
    cooldown_multiplier = models.FloatField(default=1)
    cooldown_override = models.IntegerField(blank=True, null=True)
    played_last = models.DateTimeField(auto_now_add=True)
    is_on_request_only = models.BooleanField(default=False, db_index=True)
    request_only_end = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(blank=True, null=True)
    last_played = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True
