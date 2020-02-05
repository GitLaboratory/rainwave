from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from datetime import timedelta


def default_history_trim():
    return timedelta(weeks=4)


class StationQuerySet(models.QuerySet):
    def delete(self):
        raise RuntimeError("Do not delete stations.")


class Station(models.Model):
    objects = models.Manager.from_queryset(StationQuerySet)

    name = models.CharField(max_length=64)
    directories = ArrayField(
        base_field=models.CharField(max_length=1024),
        default=list,
        help_text="Array of directories containing MP3s for this station.",
    )
    is_default = models.BooleanField(
        default=False,
        help_text="If true, this is the station that shows up for people first visiting your site.",
    )
    position = models.SmallIntegerField(
        default=0, help_text="What position in the menu this station sits at."
    )
    hostname = models.CharField(
        max_length=1024,
        help_text=(
            "Domain/subdomain for this station.  Useful if you have more than 1 station."
            "If you only have 1 station, set this to your primary domain name."
        ),
    )
    primary_relay_hostname = models.CharField(
        max_length=1024,
        help_text=(
            "Domain name that has address records for all your Icecast servers."
            "If you only have 1 Icecast server, put it here."
            "If you don't understand, put your primary Icecast server here."
        ),
    )
    primary_relay_port = models.SmallIntegerField(default=80)
    icecast_mount_name = models.CharField(
        max_length=1024,
        help_text="e.g. If your audio is at http://icecast/station.mp3, enter 'station' here. This is your 'mount' option in Icecast/LiquidSoap minus .mp3.",
    )
    planned_elections = models.SmallIntegerField(
        default=2,
        help_text="Default number of elections to plan and display on the site at once.",
    )
    default_songs_in_election = models.SmallIntegerField(
        default=3, help_text="Default number of songs in an election."
    )

    request_interval = models.SmallIntegerField(
        default=1,
        help_text="Default number of random-song-only elections to put in between elections with requests.",
    )
    events_to_next_request = models.SmallIntegerField(
        default=0, help_text="Used to keep track of when to allow requests to be used.",
    )
    request_sequence_scale = models.SmallIntegerField(
        default=5,
        help_text="How many users in the request line until we start increasing sequential elections with requests?",
    )
    request_tunein_timeout = models.IntegerField(
        default=600,
        help_text="How long after a user tunes out until they lose their place in the request line?",
    )
    request_numsong_timeout = models.SmallIntegerField(
        default=2,
        help_text="How many songs can a user sit at the head of the request line without a song before losing their place?",
    )
    song_lookup_length_delta = models.IntegerField(
        default=30,
        help_text="Elections first try to find songs of similar length - this defines how similar, in seconds.",
    )

    cooldown_percentage = models.FloatField(default=0.6)
    cooldown_highest_rating_multiplier = models.FloatField(default=0.6)
    cooldown_size_min_multiplier = models.FloatField(default=0.4)
    cooldown_size_max_multiplier = models.FloatField(default=1.0)
    cooldown_size_slope = models.FloatField(default=0.1)
    cooldown_size_slope_start = models.FloatField(default=20)
    cooldown_song_min_multiplier = models.FloatField(default=0.3)
    cooldown_song_max_multiplier = models.FloatField(default=3.3)
    cooldown_request_only_period = models.IntegerField(default=1800)

    stream_suffix = models.CharField(
        max_length=1024,
        help_text="Suffix to add to song titles when using LiquidSoap.",
    )

    tunein_partner_key = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        help_text="Use if you have an entry on TuneIn.com that you want updated",
    )
    tunein_partner_id = models.IntegerField(blank=True, null=True)
    tunein_id = models.IntegerField(blank=True, null=True)

    liquidsoap_socket_path = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        help_text="Allows you to control LiquidSoap from /admin/dj (e.g. skip song) and allows for DJs.",
    )
    liquidsoap_harbor_host = models.CharField(max_length=1024, blank=True, null=True)
    liquidsoap_harbor_port = models.IntegerField(blank=True, null=True)
    liquidsoap_harbor_mount = models.CharField(max_length=1024)

    trim_events_after = models.DurationField(default=default_history_trim)
    trim_song_history_after = models.DurationField(default=default_history_trim)

    def delete(self):
        raise RuntimeError("Do not delete stations.")

    class Meta:
        ordering = ["position", "id"]


class Relay(models.Model):
    PROTOCOL_CHOICES = (
        ("http://", "http://"),
        ("https://", "https://"),
    )

    admin_password = models.CharField(max_length=1024)
    admin_username = models.CharField(max_length=1024)
    hostname = models.CharField(max_length=1024)
    ip_address = models.CharField(max_length=256)
    listclients_url = models.CharField(max_length=1024, default="/admin/listclients")
    port = models.SmallIntegerField()
    protocol = models.CharField(max_length=64, choices=PROTOCOL_CHOICES)
    stations = models.ManyToManyField(Station)


class Donation(models.Model):
    user = models.ForeignKey(
        get_user_model(), blank=True, null=True, on_delete=models.SET_NULL
    )

    amount = models.FloatField()
    message = models.TextField(default="")
    private = models.BooleanField(default=False)
    when = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        if self.user:
            return f"Donation By {self.user.name} For {self.amount}"
        return f"Donation By Anonymous For {self.amount}"


class ListenerCount(models.Model):
    when = models.DateTimeField(auto_now_add=True)
    active_guests = models.IntegerField()
    active_users = models.IntegerField()
    guests = models.IntegerField()
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    users = models.IntegerField()

    class Meta:
        ordering = ["-when"]

    def __str__(self):
        return f"Listener Count For {self.station.name}"
