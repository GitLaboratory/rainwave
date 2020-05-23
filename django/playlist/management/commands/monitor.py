import os
import os.path
import logging
import sys

import pyinotify
from pyinotify import ProcessEvent, IN_DELETE, IN_MOVED_FROM

from django.conf import settings

from config.models import MusicDirectoryToStation, MusicDirectory
from playlist.models import ScanError

from ._base_scan import ScannerCommand, ScannerMixin

DELETE_OPERATIONS = (IN_DELETE, IN_MOVED_FROM)

log = logging.getLogger(__name__)


class NewDirectoryException(Exception):
    pass


class DeletedDirectoryException(Exception):
    pass


class FileEventHandler(ProcessEvent, ScannerMixin):
    def process_IN_ATTRIB(self, event):
        # ATTRIB events are:
        # - Some file renames (see: WinSCP)
        # - Directories when they've been touched

        # ATTRIB on directories causes full station rescans when directories are copied to the root
        # of a station.  As such, we have to ignore these.
        if event.dir:
            log.debug(f"Ignoring attrib event for directory {event.pathname}")
            return

        self._process(event)

    def process_IN_CREATE(self, event):
        if event.dir:
            self._process(event)

    def process_IN_CLOSE_WRITE(self, event):
        if event.dir:
            log.debug(f"Ignoring close write event for directory {event.pathname}")
            return
        self._process(event)

    def process_IN_DELETE(self, event):
        # Ignore WinSCP events.
        if event.pathname.endswith(".filepart"):
            return

        # Deletes are performed on files first, rendering a directory scan pointless.
        if event.dir:
            raise DeletedDirectoryException

        if not self.is_song(event.pathname):
            log.debug(f"Ignoring delete event for non-MP3 {event.pathname}")
            return

        self._process(event)

    def process_IN_MOVED_TO(self, event):
        self._process(event)

        if event.dir:
            raise NewDirectoryException

    def process_IN_MOVED_FROM(self, event):
        if not event.dir and not self.is_song(event.pathname):
            log.debug(f"Ignoring moved-from event for non-MP3 {event.pathname}")
            return

        self._process(event)

    def process_IN_MOVED_SELF(self, event):
        raise DeletedDirectoryException

    def _process(self, event):
        # Ignore WinSCP events.
        if event.pathname.endswith(".filepart"):
            return

        dirname = os.path.dirname(event.pathname)
        stations = set()
        primary_station = None
        for (
            music_directory_to_station
        ) in MusicDirectoryToStation.objects.select_related(
            "music_directory__primary_station", "station"
        ).all():
            music_directory = music_directory_to_station.music_directory
            if music_directory.path.startswith(dirname):
                stations.add(music_directory.station)
                if not primary_station:
                    primary_station = music_directory.primary_station
                elif primary_station != music_directory.primary_station:
                    message = f"Overlapping or conflicting primary directories exist for {primary_station} and {music_directory.primary_station}."
                    ScanError.objects.create(path=event.pathname, error=message)
                    raise ValueError(message)

        log.debug(
            f"{event.maskname} {event.pathname} {[station.name for station in stations]}"
        )

        try:
            if event.dir:
                self.scan_directory(event.pathname, primary_station, stations)
            elif not stations or event.mask in DELETE_OPERATIONS:
                self.disable_song(event.pathname)
            else:
                self.scan_file(event.pathname, primary_station, stations)

            self.flush_art_queue()
        except Exception as e:
            ScanError.objects.create(filename=event.pathname, error=str(e))
            log.exception(str(e), exc_info=sys.exc_info())


class Command(ScannerCommand):
    help = "Continuously scans for music changes."

    def handle(self, *args, **options):
        if settings.RW_PID_DIR:
            pid = os.getpid()
            pid_file = open(f"{settings.RW_PID_DIR}/scanner.pid", "w")
            pid_file.write(str(pid))
            pid_file.close()

        mask = (
            pyinotify.IN_ATTRIB
            | pyinotify.IN_CREATE
            | pyinotify.IN_CLOSE_WRITE
            | pyinotify.IN_DELETE
            | pyinotify.IN_MOVED_TO
            | pyinotify.IN_MOVED_FROM
            | pyinotify.IN_MOVE_SELF
            | pyinotify.IN_EXCL_UNLINK
        )

        try:
            go = True
            while go:
                try:
                    log.info("File monitor started.")
                    wm = pyinotify.WatchManager()
                    for music_directory in MusicDirectory.objects.all():
                        wm.add_watch(
                            music_directory.path, mask, rec=True, auto_add=True
                        )
                    pyinotify.Notifier(wm, FileEventHandler()).loop()
                    go = False
                except NewDirectoryException:
                    log.debug("New directory added, restarting watch.")
                except DeletedDirectoryException:
                    log.debug("Directory was deleted, restarting watch.")
                finally:
                    try:
                        wm.close()
                    except:
                        pass
        finally:
            log.info("File monitor shutdown.")
