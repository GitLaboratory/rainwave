import calendar
import time

import api.web
import api_requests.playlist
import tornado.escape
import tornado.web
from api import fieldtypes
from api.urls import handle_url
from libs import config, db


def write_html_time_form(request, html_id, at_time=None):
    current_time = calendar.timegm(time.gmtime())
    if not at_time:
        at_time = current_time
    request.write(
        request.render_string(
            "admin_time_select.html", at_time=at_time, html_id=html_id
        )
    )


@handle_url("/admin")
class AdminRedirect(tornado.web.RequestHandler):
    help_hidden = True

    def prepare(self):
        self.redirect("/admin/", permanent=True)


@handle_url("/admin/")
class AdminIndex(api.web.HTMLRequest):
    admin_required = True

    def get(self):
        self.render(
            "admin_frame.html",
            title="Rainwave Admin",
            api_url=config.get("api_external_url_prefix"),
            user_id=self.user.id,
            api_key=self.user.ensure_api_key(),
            sid=self.sid,
            tool_list_url="tool_list",
            station_list_url="station_list",
        )


@handle_url("/admin/tool_list")
class ToolList(api.web.HTMLRequest):
    admin_required = True

    def get(self):
        self.write(self.render_string("bare_header.html", title="Tool List"))
        self.write("<b>Do:</b><br />")
        for item in [
            ("Scan Results", "scan_results"),
            ("Producers", "producers"),
            ("Producers (Meta)", "producers_all"),
            ("Power Hours", "power_hours"),
            ("Cooldown", "cooldown"),
            ("Request Only Songs", "song_request_only"),
            ("Donations", "donations"),
            ("Associate Groups", "associate_groups"),
            ("Disassociate Groups", "disassociate_groups"),
            ("Edit Groups", "group_edit"),
            ("Listener Count", "listener_stats"),
            ("Listener Count [Wkly]", "listener_stats_aggregate"),
            ("JS Errors", "js_errors"),
        ]:
            self.write(
                '<a style=\'display: block\' id="%s" href="#" onclick="window.top.current_tool = \'%s\'; window.top.change_screen();">%s</a>'
                % (item[1], item[1], item[0])
            )
        self.write(self.render_string("basic_footer.html"))


@handle_url("/admin/station_list")
class StationList(api.web.HTMLRequest):
    admin_required = True

    def get(self):
        self.write(self.render_string("bare_header.html", title="Station List"))
        self.write("<b>On station:</b><br>")
        for sid in config.station_ids:
            self.write(
                '<a style=\'display: block\' id="sid_%s" href="#" onclick="window.top.current_station = %s; window.top.change_screen();">%s</a>'
                % (sid, sid, config.station_id_friendly[sid])
            )
        self.write(self.render_string("basic_footer.html"))


class AlbumList(api.web.HTMLRequest):
    admin_required = True
    allow_get = True
    allow_sid_zero = True
    fields = {"restrict": (fieldtypes.sid, True), "sort": (fieldtypes.string, None)}

    def get(self):
        self.write(self.render_string("bare_header.html", title="Album List"))
        self.write(
            "<h2>%s Playlist</h2>"
            % config.station_id_friendly[self.get_argument("restrict")]
        )
        self.write("<table>")
        sql = (
            "SELECT r4_albums.album_id AS id, album_name AS name, album_name_searchable AS name_searchable, album_rating AS rating, album_cool AS cool, album_cool_lowest AS cool_lowest, album_updated AS updated, album_fave AS fave, album_rating_user AS rating_user, album_cool_multiply AS cool_multiply, album_cool_override AS cool_override "
            "FROM r4_albums "
            "JOIN r4_album_sid USING (album_id) "
            "LEFT JOIN r4_album_ratings ON (r4_album_sid.album_id = r4_album_ratings.album_id AND r4_album_ratings.user_id = %s AND r4_album_ratings.sid = r4_album_sid.sid) "
            "LEFT JOIN r4_album_faves ON (r4_album_sid.album_id = r4_album_faves.album_id AND r4_album_faves.user_id = %s) "
            "WHERE r4_album_sid.sid = %s AND r4_album_sid.album_exists = TRUE "
        )
        if self.get_argument("sort", None) and self.get_argument("sort") == "added_on":
            sql += "ORDER BY album_newest_song_time DESC, album_name"
        else:
            sql += "ORDER BY album_name"
        albums = db.c.fetch_all(
            sql, (self.user.id, self.user.id, self.get_argument("restrict"))
        )
        for row in albums:
            self.write("<tr><td>%s</td>" % row["id"])
            self.write(
                "<td onclick=\"window.location.href = '../song_list/' + window.top.current_tool + '?sid=%s&id=%s&sort=%s';\" style='cursor: pointer;'>%s</td><td>"
                % (
                    self.get_argument("restrict"),
                    row["id"],
                    self.get_argument("sort", ""),
                    tornado.escape.xhtml_escape(row["name"]),
                )
            )
            if row["rating_user"]:
                self.write(str(row["rating_user"]))
            self.write("</td><td>(%s)</td><td>" % row["rating"])
            if row["fave"]:
                self.write("Fave")
            self.write("</td>")
            self.render_row_special(row)
            self.write("</tr>")
        self.write(self.render_string("basic_footer.html"))

    def render_row_special(self, row):
        pass


class SongList(api.web.PrettyPrintAPIMixin, api_requests.playlist.AlbumHandler):
    admin_required = True
    allow_sid_zero = True
    # fields are handled by AlbumHandler

    def get(self):  # pylint: disable=method-hidden
        self.write(self.render_string("bare_header.html", title="Song List"))
        self.write(
            "<h2>%s (%s)</h2>"
            % (self._output["album"]["name"], config.station_id_friendly[self.sid])
        )
        self.write("<table>")
        for row in self._output["album"]["songs"]:
            self.write(
                "<tr><td>%s</th><td>%s</td>"
                % (row["id"], tornado.escape.xhtml_escape(row["title"]))
            )
            if row["rating"]:
                self.write("<td>(%s)</td>" % row["rating"])
            elif "rating" in row:
                self.write("<td></td>")
            if row["rating_user"]:
                self.write("<td>%s</td>" % str(row["rating_user"]))
            elif "rating_user" in row:
                self.write("<td></td>")
            if row["fave"]:
                self.write("<td>Your Fave</td>")
            elif "fave" in row:
                self.write("<td></td>")
            if row["length"]:
                self.write(
                    "<td>{}:{:0>2d}</td>".format(
                        int(row["length"] / 60), row["length"] % 60
                    )
                )
            elif "length" in row:
                self.write("<td></td>")
            if row["added_on"]:
                self.write(
                    "<td>%sd</td>" % int((time.time() - row["added_on"]) / 86400)
                )
            elif "added_on" in row:
                self.write("<td></td>")
            if row["origin_sid"]:
                self.write(
                    "<td>%s</td>" % config.station_id_friendly[row["origin_sid"]]
                )
            elif "origin_sid" in row:
                self.write("<td></td>")
            self.render_row_special(row)
            self.write("</tr>")
        self.write(self.render_string("basic_footer.html"))

    def render_row_special(self, row):
        pass
