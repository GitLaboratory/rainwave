from playlist.models import ScanError, Song
from config.models import MusicDirectory

from ._base_scan import ScannerCommand, ScannerMixin


class Command(ScannerCommand, ScannerMixin):
    help = "Performs a one-time scan of all directories."
    scan_art_immediately = False
    song_count = 0

    def add_arguments(self, parser):
        parser.add_argument(
            "--full",
            action="store_true",
            help="Resets the playlist so that all files get re-scanned fresh.",
        )

    def handle(self, *args, **options):
        if options.get("full"):
            Song.objects.all().update(file_mtime=0)

        for music_directory in (
            MusicDirectory.objects.select_related("primary_station").all().iterator()
        ):
            self.scan_directory(
                music_directory.path,
                music_directory.primary_station,
                list(music_directory.stations.all()),
            )

        ScanError.trim()

        self.flush_art_queue()

        print()
        print(f"Done.")
        print()

    def scan_song(self, filename, primary_station, stations):
        super().scan_song(filename, primary_station, stations)
        self.song_count += 1
        print(f"{primary_station.name} - {self.song_count}", end="\r")

    def flush_art_queue(self):
        for index, filename in enumerate(self.album_art_queue):
            print(f"Scanning album art - {index}", end="\r")
            self._scan_image(filename)
