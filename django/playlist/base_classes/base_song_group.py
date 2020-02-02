from django.db.models import Model


class BaseSongGroup(Model):
    class Meta:
        abstract = True
