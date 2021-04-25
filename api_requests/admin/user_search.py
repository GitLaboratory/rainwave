from libs import db
import api.web
from api.urls import handle_api_url
from api import fieldtypes
from api.exceptions import APIException


@handle_api_url("user_search")
class UserSearchRequest(api.web.APIHandler):
    description = "Returns a user ID and station they're currently tuned to based on the username provided."
    fields = {"username": (fieldtypes.string, True)}
    auth_required = False
    sid_required = False
    help_hidden = True

    def post(self):
        if self.request.remote_ip != "127.0.0.1" and self.request.remote_ip != "::1":
            raise APIException("auth_failed", f"{self.request.remote_ip} is not allowed to access this endpoint.")

        possible_id = db.c.fetch_var(
            "SELECT user_id FROM phpbb_users WHERE username = %s OR radio_username = %s",
            (self.get_argument("username"), self.get_argument("username")),
        )
        if possible_id:
            possible_sid = db.c.fetch_var(
                "SELECT sid FROM r4_listeners WHERE user_id = %s", (possible_id,)
            )
            self.append("user", {"user_id": possible_id, "sid": possible_sid})
        else:
            self.append("user", {"user_id": None, "sid": None})

@handle_api_url("user_search_by_discord_user_id")
class UserSearchByDiscordUserIdRequest(api.web.APIHandler):
    auth_required = False
    sid_required = False
    description = "Accessible only to localhost connections, for wormgas."
    help_hidden = True
    fields = {"discord_user_id": (fieldtypes.string, True)}

    def post(self):
        if self.request.remote_ip != "127.0.0.1" and self.request.remote_ip != "::1":
            raise APIException("auth_failed", f"{self.request.remote_ip} is not allowed to access this endpoint.")

        possible_id = db.c.fetch_var(
            "SELECT user_id FROM phpbb_users WHERE discord_user_id = %s",
            (self.get_argument("discord_user_id"),),
        )
        if possible_id:
            possible_sid = db.c.fetch_var(
                "SELECT sid FROM r4_listeners WHERE user_id = %s", (possible_id,)
            )
            self.append("user", {"user_id": possible_id, "sid": possible_sid})
        else:
            self.append("user", {"user_id": None, "sid": None})
