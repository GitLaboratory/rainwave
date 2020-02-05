from django.db import models
from django.contrib.auth import get_user_model

from playlist.models import SongOnStation
from schedule.models.event import Event


class ElectionEntryTypes(object):
    CONFLICT = 0
    WARNING = 1
    NORMAL = 2
    QUEUE = 3
    REQUEST = 4


ELECTION_ENTRY_TYPES_MODEL_CHOICES = [
    (ElectionEntryTypes.CONFLICT, "Conflict"),
    (ElectionEntryTypes.WARNING, "Warning"),
    (ElectionEntryTypes.NORMAL, "Normal"),
    (ElectionEntryTypes.QUEUE, "Queue"),
    (ElectionEntryTypes.REQUEST, "Request"),
]


class Election(Event):
    pass


class ElectionEntry(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    song_on_station = models.ForeignKey(SongOnStation, on_delete=models.CASCADE)
    entry_type = models.SmallIntegerField(
        default=ElectionEntryTypes.NORMAL, choices=ELECTION_ENTRY_TYPES_MODEL_CHOICES
    )
    position = models.SmallIntegerField()
    votes = models.SmallIntegerField(default=0)


class Vote(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    election_entry = models.ForeignKey(
        ElectionEntry, on_delete=models.SET_NULL, blank=True, null=True
    )
    song_on_station = models.ForeignKey(SongOnStation, on_delete=models.CASCADE)
    when = models.DateTimeField(auto_now_add=True)
