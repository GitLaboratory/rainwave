from django.db import models
from django.contrib.auth import get_user_model


class Producer(models.Model):
    name = models.CharField(max_length=1024)
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    ended_at = models.DateTimeField(blank=True, null=True)
    in_progress = models.BooleanField(default=False)
    used = models.BooleanField(default=False, db_index=True)
    url = models.CharField(max_length=2048, blank=True, null=True)
    use_crossfade = models.BooleanField(default=True)

    # dj = models.ForeignKey(
    #     get_user_model(),
    #     models.SET_NULL,
    #     blank=True,
    #     null=True,
    #     related_name="dj_event_set",
    # )
    creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_event_set",
    )
