from django.db import models
from django.contrib.auth import get_user_model

from utils.generate_key import generate_key


class APIKey(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    key = models.CharField(default=generate_key, max_length=10, db_index=True)
