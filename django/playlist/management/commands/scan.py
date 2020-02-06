import os
import mimetypes

from django.core.management.base import BaseCommand

from playlist.models import Song
from config.models import MusicDirectory

mimetypes.init()


class Command(BaseCommand):
    help = "Performs a one-time scan of all directories."

    def handle(self, *args, **options):
        for directory in (
            MusicDirectory.objects.select_related("primary_station").all().iterator()
        ):
            known_songs = Song.objects.filter(filename__startswith=directory.path)
            known_songs.update(scanned=False)

            for root, _subdirs, files in os.walk(directory, followlinks=True):
                for filename in files:
                    filetypes = mimetypes.guess_type(filename)
                    if any(
                        filetype in ("audio/x-mpg", "audio/mpeg")
                        for filetype in filetypes
                    ):
                        Song.scan(
                            os.path.join(root, filename),
                            directory.primary_station,
                            directory.stations.all(),
                        )

            for song in known_songs.filter(scanned=False).iterator():
                song.disable()
