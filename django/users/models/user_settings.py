from django.db import models
from django.contrib.auth import get_user_model

from utils.generate_key import generate_key


class UserSettings(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name="settings"
    )

    inactive = models.BooleanField(default=False, blank=True, null=True,)
    donor = models.BooleanField(default=False)
    last_active = models.IntegerField(default=0, blank=True, null=True,)
    listen_key = models.TextField(default=generate_key, blank=True, null=True,)
    losing_requests = models.IntegerField(default=0, blank=True, null=True,)
    losing_votes = models.IntegerField(default=0, blank=True, null=True,)
    requests_paused = models.BooleanField(default=False, blank=True, null=True,)
    total_mind_changes = models.IntegerField(default=0, blank=True, null=True,)
    total_ratings = models.IntegerField(default=0, blank=True, null=True,)
    total_requests = models.IntegerField(default=0, blank=True, null=True,)
    total_votes = models.IntegerField(default=0, blank=True, null=True,)
    winning_requests = models.IntegerField(default=0, blank=True, null=True,)
    winning_votes = models.IntegerField(default=0, blank=True, null=True,)
