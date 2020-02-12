import os
import mimetypes
import mutagen

from django.core.management.base import BaseCommand

from playlist.models import Song, ScanError
from playlist.exceptions import ScanMetadataException
from config.models import MusicDirectory

mimetypes.init()

SKIPPABLE_EXCEPTIONS = (ScanMetadataException, mutagen.mp3.HeaderNotFoundError)


class Command(BaseCommand):
    help = "Performs a one-time scan of all directories."

    def handle(self, *args, **options):
        for directory in (
            MusicDirectory.objects.select_related("primary_station").all().iterator()
        ):
            known_songs = Song.objects.filter(filename__startswith=directory.path)
            known_songs.update(scanned=False)

            errors_encountered = 0
            song_number = 0
            for root, _subdirs, files in os.walk(directory.path, followlinks=True):
                for filename in files:
                    filetypes = mimetypes.guess_type(filename)
                    if any(
                        filetype in ("audio/x-mpg", "audio/mpeg")
                        for filetype in filetypes
                    ):
                        full_filename = os.path.join(root, filename)
                        try:
                            song_number += 1
                            print(f"{directory.path} song {song_number}", end="\r")
                            Song.scan(
                                filename=full_filename,
                                origin_station=directory.primary_station,
                                stations=directory.stations.all(),
                            )
                        except SKIPPABLE_EXCEPTIONS as e:
                            ScanError.objects.create(
                                filename=full_filename, error=str(e),
                            )
                            errors_encountered += 1
                        except ValueError as e:
                            if "0x00" in str(e):
                                ScanError.objects.create(
                                    filename=full_filename, error=str(e)
                                )
                                errors_encountered += 1
                            else:
                                raise

            print(f"{directory.path} cleaning up...")
            for song in known_songs.filter(scanned=False).iterator():
                song.disable()

        ScanError.trim()

        print(f"Done.  {errors_encountered} errors encountered.")
