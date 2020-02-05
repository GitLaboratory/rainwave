from django.db import models


class ObjectWithVoteStats(models.Model):
    vote_count = models.IntegerField(default=0)
    vote_share = models.FloatField(blank=True, null=True)
    votes_seen = models.IntegerField(default=0)

    class Meta:
        abstract = True
