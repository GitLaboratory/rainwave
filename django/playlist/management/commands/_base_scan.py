import os
import mimetypes
import psutil
import mutagen
from PIL import Image

from django.core.management.base import BaseCommand
from django.conf import settings

from playlist.models import Song, ScanError, AlbumOnStation
from playlist.exceptions import ScanMetadataException

mimetypes.init()

SKIPPABLE_EXCEPTIONS = (ScanMetadataException, mutagen.mp3.HeaderNotFoundError)


IGNORE_FILE_EXTENSIONS = (".tmp", ".filepart")

# This is a tuple of "art size" to _actual_ size used on Rainwave.
# We've increased the actual size of album art over the years, but we cannot break
# backwards compatibility with existing API clients.
ALBUM_ART_DIMENSIONS = ((360, 480), (240, 240), (120, 240))


class ScannerMixin:
    scan_art_immediately = False
    album_art_queue = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scan_art_immediately = False
        self.album_art_queue = []

    def scan_directory(self, path, primary_station, stations):
        known_songs = Song.objects.filter(filename__startswith=path)
        known_songs.update(scanned=False)

        if os.stat(path):
            for root, _subdirs, files in os.walk(path, followlinks=True):
                for bare_filename in files:
                    self.scan_file(
                        filename=os.path.join(root, bare_filename),
                        primary_station=primary_station,
                        stations=stations,
                    )

        for song in known_songs.filter(scanned=False).iterator():
            song.disable()

    def is_song(self, filename):
        filetypes = mimetypes.guess_type(filename)
        return any(filetype in ("audio/x-mpg", "audio/mpeg") for filetype in filetypes)

    def is_art(self, filename):
        filetypes = mimetypes.guess_type(filename)
        return settings.RW_SCANNER_ALBUM_ART_ENABLED and any(
            filetype.startswith("image/") for filetype in filetypes
        )

    def scan_file(self, filename, primary_station, stations):
        if filename.split(".")[-1].lower() in IGNORE_FILE_EXTENSIONS:
            return None

        if self.is_song(filename):
            self.scan_song(filename, primary_station, stations)
        elif self.is_art(filename):
            self.scan_art(filename)

    def scan_song(self, filename, primary_station, stations):
        self.scan_art_immediately = False
        try:
            Song.scan(
                filename=filename, origin_station=primary_station, stations=stations,
            )
        except SKIPPABLE_EXCEPTIONS as e:
            ScanError.objects.create(
                filename=filename, error=str(e),
            )
        except ValueError as e:
            if "0x00" in str(e):
                ScanError.objects.create(filename=filename, error=str(e))
            else:
                raise

    def disable_song(self, filename):
        song = Song.objects.filter(filename=filename).first()
        if song:
            song.disable()

    def _scan_image(self, filename):
        if not settings.RW_SCANNER_ALBUM_ART_ENABLED:
            return

        album_on_stations = AlbumOnStation.objects.select_related("station").filter(
            album__song_set__filename__startswith=os.path.dirname(filename)
        )
        if not album_on_stations.exists():
            return

        try:
            im_original = Image.open(filename)
            if not im_original:
                raise IOError
            if im_original.mode != "RGB":
                im_original = im_original.convert()
            if (
                im_original.size[0] < ALBUM_ART_DIMENSIONS[0][1]
                or im_original.size[1] < ALBUM_ART_DIMENSIONS[0][1]
            ):
                ScanError.objects.create(
                    filename=filename,
                    error=f"Small album art warning. {im_original.size[0]}x{im_original.size[1]}",
                )
            for (filename_suffix, size) in ALBUM_ART_DIMENSIONS:
                im = im_original
                if im_original.size[0] > size or im_original.size[1] > size:
                    im = im_original.copy()
                    im.thumbnail((size, size), Image.ANTIALIAS)

                for album_on_station in album_on_stations:
                    im.save(
                        os.path.join(
                            settings.RW_SCANNER_ALBUM_ART_DESTINATION_PATH,
                            f"{album_on_station.station_id}_{album_on_station.album_id}_{filename_suffix}.jpg",
                        )
                    )
                    if album_on_station.station.is_default:
                        im.save(
                            os.path.join(
                                settings.RW_SCANNER_ALBUM_ART_DESTINATION_PATH,
                                f"a_{album_on_station.album_id}_{filename_suffix}.jpg",
                            )
                        )
        except (IOError, OSError):
            ScanError.objects.create(
                filename=filename,
                error="Could not open album art. (this will happen when a directory has been deleted)",
            )
        except Exception as e:
            # Pillow throws a lot of standard exceptions for its routines, e.g. EOFError
            # It's really hard to catch them all, so just catch all of them.
            ScanError.objects.create(filename=filename, error=str(e))

    def scan_art(self, filename):
        if not self.scan_art_immediately:
            self.album_art_queue.append(filename)
            return
        self._scan_image(filename)

    def flush_art_queue(self):
        for filename in self.album_art_queue:
            self._scan_image(filename)
        self.scan_art_immediately = True


class ScannerCommand(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            p = psutil.Process(os.getpid())
            p.set_nice(10)
        except:
            pass

        try:
            p = psutil.Process(os.getpid())
            p.set_ionice(psutil.IOPRIO_CLASS_IDLE)
        except:
            pass
