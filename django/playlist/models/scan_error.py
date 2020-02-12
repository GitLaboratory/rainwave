import datetime

from django.db import models


class ScanError(models.Model):
    filename = models.TextField()
    error = models.TextField()
    when = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    @classmethod
    def trim(cls):
        cls.objects.filter(
            when__lt=datetime.datetime.now() - datetime.timedelta(weeks=2)
        )
