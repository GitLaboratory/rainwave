from django.db import models


class Artist(models.Model):
    id = models.AutoField(primary_key=True, db_column="artist_id")
    name = models.TextField(blank=True, null=True, db_column="artist_name")
    name_searchable = models.TextField(db_column="artist_name_searchable")

    class Meta:
        managed = False
        db_table = "r4_artists"
