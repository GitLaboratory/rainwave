from django.db import models
from django.contrib.auth.models import AbstractUser

from utils.generate_key import generate_key


class User(AbstractUser):
    id = models.AutoField(primary_key=True, db_column="user_id")
    username = models.TextField(
        blank=True, null=True, db_column="username", unique=True
    )
    email = models.TextField(blank=True, null=True, db_column="user_email")

    # TODO: these need to be added manually right now as they don't exist in Rainwave but HAVE to exist for Django
    is_staff = models.BooleanField(default=False, db_column="is_staff")
    is_superuser = models.BooleanField(default=False, db_column="is_superuser")
    is_active = models.BooleanField(default=True, db_column="is_active")

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["phpbb_group_id"]

    inactive = models.BooleanField(
        default=False, blank=True, null=True, db_column="radio_inactive"
    )
    last_active = models.IntegerField(
        default=0, blank=True, null=True, db_column="radio_last_active"
    )
    listen_key = models.TextField(
        default=generate_key, blank=True, null=True, db_column="radio_listenkey"
    )
    losing_requests = models.IntegerField(
        default=0, blank=True, null=True, db_column="radio_losingrequests"
    )
    losing_votes = models.IntegerField(
        default=0, blank=True, null=True, db_column="radio_losingvotes"
    )
    requests_paused = models.BooleanField(
        default=False, blank=True, null=True, db_column="radio_requests_paused"
    )
    total_mind_changes = models.IntegerField(
        default=0, blank=True, null=True, db_column="radio_totalmindchange"
    )
    total_ratings = models.IntegerField(
        default=0, blank=True, null=True, db_column="radio_totalratings"
    )
    total_requests = models.IntegerField(
        default=0, blank=True, null=True, db_column="radio_totalrequests"
    )
    total_votes = models.IntegerField(
        default=0, blank=True, null=True, db_column="radio_totalvotes"
    )
    winning_requests = models.IntegerField(
        default=0, blank=True, null=True, db_column="radio_winningrequests"
    )
    winning_votes = models.IntegerField(
        default=0, blank=True, null=True, db_column="radio_winningvotes"
    )

    phpbb_avatar = models.TextField(
        editable=False, blank=True, null=True, db_column="user_avatar"
    )
    phpbb_avatar_type = models.IntegerField(
        editable=False, blank=True, null=True, db_column="user_avatar_type"
    )
    phpbb_colour = models.TextField(
        editable=False, blank=True, null=True, db_column="user_colour"
    )
    phpbb_group_id = models.IntegerField(
        editable=False, blank=True, null=True, db_column="group_id"
    )
    phpbb_new_privmsg = models.IntegerField(
        editable=False, blank=True, null=True, db_column="user_new_privmsg"
    )
    phpbb_rank = models.IntegerField(
        editable=False, blank=True, null=True, db_column="user_rank"
    )
    phpbb_regdate = models.IntegerField(
        editable=False, blank=True, null=True, db_column="user_regdate"
    )

    def set_password(self, *args, **kwargs):
        raise NotImplementedError

    def check_password(self, *args, **kwargs):
        raise NotImplementedError

    @property
    def last_login(self):
        return None

    @property
    def date_joined(self):
        return None

    class Meta:
        managed = False
        db_table = "phpbb_users"
        ordering = ["username"]
