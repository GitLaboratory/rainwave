from django.db import models

from users.models.user import User

from utils.generate_key import generate_key
from utils.time import now


class APIKey(models.Model):
    id = models.AutoField(primary_key=True, db_column="api_id")
    user = models.ForeignKey(User, models.CASCADE, db_column="user_id")

    key = models.CharField(
        default=generate_key, max_length=10, db_column="api_key", db_index=True
    )

    expires_on = models.IntegerField(blank=True, null=True, db_column="api_expiry")
    listen_key = models.TextField(
        default=generate_key, blank=True, null=True, db_column="api_key_listen_key"
    )

    class Meta:
        managed = False
        db_table = "r4_api_keys"

    def save(self, *args, **kwargs):
        if self.user.is_anonymous and not self.expires_on:
            self.expires_on = now() + 172800
        super().save(*args, **kwargs)
