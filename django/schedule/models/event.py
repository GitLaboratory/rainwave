from django.db import models

from config.models import Station


class Event(models.Model):
    producer = models.ForeignKey(
        "schedule.Producer", on_delete=models.SET_NULL, blank=True, null=True
    )
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    in_progress = models.BooleanField(default=False)
    start = models.DateTimeField(blank=True, null=True)

    @property
    def length(self):
        raise NotImplementedError
