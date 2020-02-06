from django.db import models
from django.contrib.auth import get_user_model

from config.models import Station


class Donation(models.Model):
    user = models.ForeignKey(
        get_user_model(), blank=True, null=True, on_delete=models.SET_NULL
    )

    amount = models.FloatField()
    message = models.TextField(default="")
    private = models.BooleanField(default=False)
    when = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        if self.user:
            return f"Donation By {self.user.name} For {self.amount}"
        return f"Donation By Anonymous For {self.amount}"


class ListenerCount(models.Model):
    when = models.DateTimeField(auto_now_add=True)
    active_guests = models.IntegerField()
    active_users = models.IntegerField()
    guests = models.IntegerField()
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    users = models.IntegerField()

    class Meta:
        ordering = ["-when"]

    def __str__(self):
        return f"Listener Count For {self.station.name}"
