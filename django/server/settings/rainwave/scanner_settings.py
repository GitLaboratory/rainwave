# Rename files that contain odd characters that will choke LiquidSoap?
RW_SCANNER_RENAME_FILES = False

# Allow songs to have the same ID3 Title and Album, with different filenames?
RW_SCANNER_ALLOW_DUPLICATE_SONGS = False

# Save tracknumbers to the database?
RW_SCANNER_SAVE_TRACKNUMBERS = True

# Normalize volume before adding?  Does not alter original MP3s.
# (requires mp3gain executable to be on the PATH)
RW_SCANNER_MP3GAIN = False

# Enable album art processing.  Requires PIL/pillow library in Python.
RW_SCANNER_ALBUM_ART_ENABLED = False

# Where to store resized album art processed by Rainwave.
RW_SCANNER_ALBUM_ART_DESTINATION_PATH = "static/album_art"

# URL that browsers will load art from.
RW_SCANNER_ALBUM_ART_EXTERNAL_URL_PATH = "/static/album_art"
