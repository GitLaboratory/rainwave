from django.db import models
from django.contrib.auth import get_user_model

from misc.models import Station, Relay


class Listener(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, blank=True, null=True,
    )
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    lock_to_station = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="+"
    )
    lock_to_station_ends_at = models.DateTimeField(blank=True, null=True)
    relay = models.ForeignKey(Relay, on_delete=models.CASCADE)

    agent = models.CharField(max_length=128)
    icecast_id = models.IntegerField()
    since = models.DateTimeField(auto_now_add=True)
