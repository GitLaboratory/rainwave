class PhpbbRanks(models.Model):
    rank_id = models.AutoField(primary_key=True)
    rank_title = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "phpbb_ranks"


class PhpbbSessionKeys(models.Model):
    key_id = models.TextField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "phpbb_session_keys"


class PhpbbSessions(models.Model):
    session_user_id = models.IntegerField(blank=True, null=True)
    session_id = models.TextField(blank=True, null=True)
    session_last_visit = models.IntegerField(blank=True, null=True)
    session_page = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "phpbb_sessions"


class PhpbbUsers(models.Model):
    user_id = models.AutoField(primary_key=True)
    group_id = models.IntegerField(blank=True, null=True)
    username = models.TextField(blank=True, null=True)
    user_new_privmsg = models.IntegerField(blank=True, null=True)
    user_avatar = models.TextField(blank=True, null=True)
    user_avatar_type = models.IntegerField(blank=True, null=True)
    user_colour = models.TextField(blank=True, null=True)
    user_rank = models.IntegerField(blank=True, null=True)
    user_regdate = models.IntegerField(blank=True, null=True)
    radio_totalvotes = models.IntegerField(blank=True, null=True)
    radio_totalmindchange = models.IntegerField(blank=True, null=True)
    radio_totalratings = models.IntegerField(blank=True, null=True)
    radio_totalrequests = models.IntegerField(blank=True, null=True)
    radio_winningvotes = models.IntegerField(blank=True, null=True)
    radio_losingvotes = models.IntegerField(blank=True, null=True)
    radio_winningrequests = models.IntegerField(blank=True, null=True)
    radio_losingrequests = models.IntegerField(blank=True, null=True)
    radio_last_active = models.IntegerField(blank=True, null=True)
    radio_listenkey = models.TextField(blank=True, null=True)
    radio_inactive = models.BooleanField(blank=True, null=True)
    radio_requests_paused = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "phpbb_users"


class R4AlbumFaves(models.Model):
    album = models.ForeignKey("R4Albums", models.DO_NOTHING)
    user = models.ForeignKey(PhpbbUsers, models.DO_NOTHING)
    album_fave = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_album_faves"


class R4AlbumRatings(models.Model):
    album = models.ForeignKey("R4Albums", models.DO_NOTHING)
    sid = models.SmallIntegerField()
    user = models.ForeignKey(PhpbbUsers, models.DO_NOTHING)
    album_rating_user = models.FloatField(blank=True, null=True)
    album_rating_complete = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_album_ratings"


class R4AlbumSid(models.Model):
    album_exists = models.BooleanField(blank=True, null=True)
    album = models.OneToOneField("R4Albums", models.DO_NOTHING, primary_key=True)
    sid = models.SmallIntegerField()
    album_song_count = models.SmallIntegerField(blank=True, null=True)
    album_played_last = models.IntegerField(blank=True, null=True)
    album_requests_pending = models.BooleanField(blank=True, null=True)
    album_cool = models.BooleanField(blank=True, null=True)
    album_cool_multiply = models.FloatField(blank=True, null=True)
    album_cool_override = models.IntegerField(blank=True, null=True)
    album_cool_lowest = models.IntegerField(blank=True, null=True)
    album_updated = models.IntegerField(blank=True, null=True)
    album_elec_last = models.IntegerField(blank=True, null=True)
    album_rating = models.FloatField()
    album_rating_count = models.IntegerField(blank=True, null=True)
    album_request_count = models.IntegerField(blank=True, null=True)
    album_fave_count = models.IntegerField(blank=True, null=True)
    album_vote_count = models.IntegerField(blank=True, null=True)
    album_votes_seen = models.IntegerField(blank=True, null=True)
    album_vote_share = models.FloatField(blank=True, null=True)
    album_newest_song_time = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_album_sid"
        unique_together = (("album", "sid"),)


class R4Albums(models.Model):
    album_id = models.AutoField(primary_key=True)
    album_name = models.TextField(blank=True, null=True)
    album_name_searchable = models.TextField()
    album_year = models.SmallIntegerField(blank=True, null=True)
    album_added_on = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_albums"


class R4ApiKeys(models.Model):
    api_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(PhpbbUsers, models.DO_NOTHING)
    api_key = models.CharField(max_length=10, blank=True, null=True)
    api_expiry = models.IntegerField(blank=True, null=True)
    api_key_listen_key = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_api_keys"


class R4Artists(models.Model):
    artist_id = models.AutoField(primary_key=True)
    artist_name = models.TextField(blank=True, null=True)
    artist_name_searchable = models.TextField()

    class Meta:
        managed = False
        db_table = "r4_artists"


class R4Donations(models.Model):
    donation_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(blank=True, null=True)
    donation_amount = models.FloatField(blank=True, null=True)
    donation_message = models.TextField(blank=True, null=True)
    donation_private = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_donations"


class R4ElectionEntries(models.Model):
    entry_id = models.AutoField(primary_key=True)
    song = models.ForeignKey("R4Songs", models.DO_NOTHING)
    elec = models.ForeignKey("R4Elections", models.DO_NOTHING)
    entry_type = models.SmallIntegerField(blank=True, null=True)
    entry_position = models.SmallIntegerField(blank=True, null=True)
    entry_votes = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_election_entries"


class R4Elections(models.Model):
    elec_id = models.AutoField(primary_key=True)
    elec_used = models.BooleanField(blank=True, null=True)
    elec_in_progress = models.BooleanField(blank=True, null=True)
    elec_start_actual = models.IntegerField(blank=True, null=True)
    elec_type = models.TextField(blank=True, null=True)
    elec_priority = models.BooleanField(blank=True, null=True)
    sid = models.SmallIntegerField()
    sched = models.ForeignKey("R4Schedule", models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_elections"


class R4GroupSid(models.Model):
    group = models.ForeignKey("R4Groups", models.DO_NOTHING, blank=True, null=True)
    sid = models.SmallIntegerField()
    group_display = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_group_sid"


class R4Groups(models.Model):
    group_id = models.AutoField(primary_key=True)
    group_name = models.TextField(blank=True, null=True)
    group_name_searchable = models.TextField()
    group_elec_block = models.SmallIntegerField(blank=True, null=True)
    group_cool_time = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_groups"


class R4ListenerCounts(models.Model):
    lc_time = models.IntegerField(blank=True, null=True)
    sid = models.SmallIntegerField()
    lc_guests = models.SmallIntegerField(blank=True, null=True)
    lc_users = models.SmallIntegerField(blank=True, null=True)
    lc_users_active = models.SmallIntegerField(blank=True, null=True)
    lc_guests_active = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_listener_counts"


class R4Listeners(models.Model):
    listener_id = models.AutoField(primary_key=True)
    sid = models.SmallIntegerField()
    listener_ip = models.TextField(blank=True, null=True)
    listener_relay = models.TextField(blank=True, null=True)
    listener_agent = models.TextField(blank=True, null=True)
    listener_icecast_id = models.IntegerField()
    listener_lock = models.BooleanField(blank=True, null=True)
    listener_lock_sid = models.SmallIntegerField(blank=True, null=True)
    listener_lock_counter = models.SmallIntegerField(blank=True, null=True)
    listener_purge = models.BooleanField(blank=True, null=True)
    listener_voted_entry = models.IntegerField(blank=True, null=True)
    listener_key = models.TextField(blank=True, null=True)
    user = models.ForeignKey(PhpbbUsers, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_listeners"


class R4OneUps(models.Model):
    one_up_id = models.AutoField()
    sched = models.ForeignKey("R4Schedule", models.DO_NOTHING)
    song = models.ForeignKey("R4Songs", models.DO_NOTHING)
    one_up_order = models.SmallIntegerField(blank=True, null=True)
    one_up_used = models.BooleanField(blank=True, null=True)
    one_up_queued = models.BooleanField(blank=True, null=True)
    one_up_sid = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = "r4_one_ups"


class R4PrefStorage(models.Model):
    user = models.ForeignKey(PhpbbUsers, models.DO_NOTHING, blank=True, null=True)
    ip_address = models.TextField(blank=True, null=True)
    prefs = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "r4_pref_storage"


class R4RequestHistory(models.Model):
    request_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(PhpbbUsers, models.DO_NOTHING)
    song = models.ForeignKey("R4Songs", models.DO_NOTHING)
    request_fulfilled_at = models.IntegerField(blank=True, null=True)
    request_wait_time = models.IntegerField(blank=True, null=True)
    request_line_size = models.IntegerField(blank=True, null=True)
    request_at_count = models.IntegerField(blank=True, null=True)
    sid = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_request_history"


class R4RequestLine(models.Model):
    user = models.OneToOneField(PhpbbUsers, models.DO_NOTHING)
    sid = models.SmallIntegerField()
    line_wait_start = models.IntegerField(blank=True, null=True)
    line_expiry_tune_in = models.IntegerField(blank=True, null=True)
    line_expiry_election = models.IntegerField(blank=True, null=True)
    line_has_had_valid = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_request_line"


class R4RequestStore(models.Model):
    reqstor_id = models.AutoField(primary_key=True)
    reqstor_order = models.SmallIntegerField(blank=True, null=True)
    user = models.ForeignKey(PhpbbUsers, models.DO_NOTHING)
    song = models.ForeignKey("R4Songs", models.DO_NOTHING)
    sid = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = "r4_request_store"


class R4Schedule(models.Model):
    sched_id = models.AutoField(primary_key=True)
    sched_start = models.IntegerField(blank=True, null=True)
    sched_start_actual = models.IntegerField(blank=True, null=True)
    sched_end = models.IntegerField(blank=True, null=True)
    sched_end_actual = models.IntegerField(blank=True, null=True)
    sched_type = models.TextField(blank=True, null=True)
    sched_name = models.TextField(blank=True, null=True)
    sched_url = models.TextField(blank=True, null=True)
    sched_dj_user = models.ForeignKey(
        PhpbbUsers, models.DO_NOTHING, blank=True, null=True
    )
    sid = models.SmallIntegerField()
    sched_public = models.BooleanField(blank=True, null=True)
    sched_timed = models.BooleanField(blank=True, null=True)
    sched_in_progress = models.BooleanField(blank=True, null=True)
    sched_used = models.BooleanField(blank=True, null=True)
    sched_use_crossfade = models.BooleanField(blank=True, null=True)
    sched_use_tag_suffix = models.BooleanField(blank=True, null=True)
    sched_creator_user_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_schedule"


class R4SongArtist(models.Model):
    song = models.ForeignKey("R4Songs", models.DO_NOTHING)
    artist = models.OneToOneField(R4Artists, models.DO_NOTHING, primary_key=True)
    artist_order = models.SmallIntegerField(blank=True, null=True)
    artist_is_tag = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_song_artist"
        unique_together = (("artist", "song"),)


class R4SongGroup(models.Model):
    song = models.ForeignKey("R4Songs", models.DO_NOTHING)
    group = models.OneToOneField(R4Groups, models.DO_NOTHING, primary_key=True)
    group_is_tag = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_song_group"
        unique_together = (("group", "song"),)


class R4SongHistory(models.Model):
    songhist_id = models.AutoField(primary_key=True)
    songhist_time = models.IntegerField(blank=True, null=True)
    sid = models.SmallIntegerField()
    song = models.ForeignKey("R4Songs", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "r4_song_history"


class R4SongRatings(models.Model):
    song = models.ForeignKey("R4Songs", models.DO_NOTHING)
    user = models.OneToOneField(PhpbbUsers, models.DO_NOTHING, primary_key=True)
    song_rating_user = models.FloatField(blank=True, null=True)
    song_rated_at = models.IntegerField(blank=True, null=True)
    song_rated_at_rank = models.IntegerField(blank=True, null=True)
    song_rated_at_count = models.IntegerField(blank=True, null=True)
    song_fave = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_song_ratings"
        unique_together = (("user", "song"),)


class R4SongSid(models.Model):
    song = models.OneToOneField("R4Songs", models.DO_NOTHING, primary_key=True)
    sid = models.SmallIntegerField()
    song_cool = models.BooleanField(blank=True, null=True)
    song_cool_end = models.IntegerField(blank=True, null=True)
    song_elec_appearances = models.IntegerField(blank=True, null=True)
    song_elec_last = models.IntegerField(blank=True, null=True)
    song_elec_blocked = models.BooleanField(blank=True, null=True)
    song_elec_blocked_num = models.SmallIntegerField(blank=True, null=True)
    song_elec_blocked_by = models.TextField(blank=True, null=True)
    song_played_last = models.IntegerField(blank=True, null=True)
    song_exists = models.BooleanField(blank=True, null=True)
    song_request_only = models.BooleanField(blank=True, null=True)
    song_request_only_end = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_song_sid"
        unique_together = (("song", "sid"),)


class R4Songs(models.Model):
    song_id = models.AutoField(primary_key=True)
    album = models.ForeignKey(R4Albums, models.DO_NOTHING, blank=True, null=True)
    song_origin_sid = models.SmallIntegerField()
    song_verified = models.BooleanField(blank=True, null=True)
    song_scanned = models.BooleanField(blank=True, null=True)
    song_filename = models.TextField(blank=True, null=True)
    song_title = models.TextField(blank=True, null=True)
    song_title_searchable = models.TextField()
    song_artist_tag = models.TextField(blank=True, null=True)
    song_url = models.TextField(blank=True, null=True)
    song_link_text = models.TextField(blank=True, null=True)
    song_length = models.SmallIntegerField(blank=True, null=True)
    song_track_number = models.SmallIntegerField(blank=True, null=True)
    song_disc_number = models.SmallIntegerField(blank=True, null=True)
    song_year = models.SmallIntegerField(blank=True, null=True)
    song_added_on = models.IntegerField(blank=True, null=True)
    song_rating = models.FloatField(blank=True, null=True)
    song_rating_count = models.IntegerField(blank=True, null=True)
    song_fave_count = models.IntegerField(blank=True, null=True)
    song_request_count = models.IntegerField(blank=True, null=True)
    song_cool_multiply = models.FloatField(blank=True, null=True)
    song_cool_override = models.IntegerField(blank=True, null=True)
    song_file_mtime = models.IntegerField(blank=True, null=True)
    song_replay_gain = models.TextField(blank=True, null=True)
    song_vote_count = models.IntegerField(blank=True, null=True)
    song_votes_seen = models.IntegerField(blank=True, null=True)
    song_vote_share = models.FloatField(blank=True, null=True)
    song_artist_parseable = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_songs"


class R4VoteHistory(models.Model):
    vote_id = models.AutoField(primary_key=True)
    vote_time = models.IntegerField(blank=True, null=True)
    elec = models.ForeignKey(R4Elections, models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(PhpbbUsers, models.DO_NOTHING)
    song = models.ForeignKey(R4Songs, models.DO_NOTHING)
    vote_at_rank = models.IntegerField(blank=True, null=True)
    vote_at_count = models.IntegerField(blank=True, null=True)
    entry = models.ForeignKey(
        R4ElectionEntries, models.DO_NOTHING, blank=True, null=True
    )
    sid = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "r4_vote_history"


class R4VoteHistoryArchived(models.Model):
    vote_id = models.AutoField(primary_key=True)
    vote_time = models.IntegerField(blank=True, null=True)
    elec = models.ForeignKey(R4Elections, models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(PhpbbUsers, models.DO_NOTHING)
    song = models.ForeignKey(R4Songs, models.DO_NOTHING)
    vote_at_rank = models.IntegerField(blank=True, null=True)
    vote_at_count = models.IntegerField(blank=True, null=True)
    entry = models.ForeignKey(
        R4ElectionEntries, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "r4_vote_history_archived"
