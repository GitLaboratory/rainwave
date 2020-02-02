class RainwaveRatingMap(object):
    threshold = 0
    points = 0

    def __init__(self, threshold, points):
        self.threshold = threshold
        self.points = points


class RainwaveStation(object):
    station_id = 0
    name = "Rainwave"
    directories = ["/home/rainwave/music"]

    # Domain/subdomain for this station.  Useful if you have more than 1 station.
    # If you only have 1 station, set this to your primary domain name.
    host = "localhost"

    # Domain name that has address records for all your Icecast servers.
    # If you only have 1 Icecast server, put it here.
    # If you don't understand, put your primary Icecast server here.
    round_robin_relay_host = "localhost"
    round_robin_relay_port = "8000"

    # If your audio is at http://icecast/station.mp3, enter 'station' here.
    # This is your 'mount' option in Icecast/LiquidSoap minus .mp3.
    stream_filename = "test"

    # Default number of elections to plan and display on the site at once.
    num_planned_elections = 2
    # Default number of songs in an election.
    songs_in_election = 3

    # Default number of random-song-only elections to put in between elections with requests.
    request_interval = 1
    # How many users in the request line until we start increasing sequential elections with requests?
    request_sequence_scale = 5
    # How long after a user tunes out until they lose their place in the request line?
    request_tunein_timeout = 600
    # How many songs can a user sit at the head of the request line without a song before losing their place?
    request_numsong_timeout = 2
    # Elections first try to find songs of similar length - this defines how similar, in seconds.
    song_lookup_length_delta = 30

    # Cooldown formula tweaking.  Recommended to leave this alone!
    cooldown_percentage = 0.6
    cooldown_highest_rating_multiplier = 0.6
    cooldown_size_min_multiplier = 0.4
    cooldown_size_max_multiplier = 1.0
    cooldown_size_slope = 0.1
    cooldown_size_slope_start = 20
    cooldown_song_min_multiplier = 0.3
    cooldown_song_max_multiplier = 3.3
    cooldown_request_only_period = 1800

    # Enable cooldowns for categrories.
    cooldown_enable_for_categories = True

    # Suffix to add to song titles when using LiquidSoap.
    stream_suffix = " [Rainwave]"

    # Use if you have an entry on TuneIn.com that you want updated
    tunein_partner_key = None
    tunein_partner_id = 0
    tunein_id = 0

    # Allows you to control LiquidSoap from /admin/dj (e.g. skip song) and allows for DJs
    liquidsoap_socket_path = "/var/run/liquidsoap/station.sock"
    liquidsoap_harbor_host = "localhost"
    liquidsoap_harbor_port = "9001"
    liquidsoap_harbor_mount = "dj.mp3"

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class RainwaveRelay(object):
    hostname = "localhost"
    ip_address = "127.0.0.1"
    protocol = "http://"
    port = 8000
    listclients_url = "/admin/listclients"
    admin_username = "admin"
    admin_password = "admin"
    station_ids = [1]

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
