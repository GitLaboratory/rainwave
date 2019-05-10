from libs import cache
import api.web
from api.server import handle_api_url
from api.server import handle_api_html_url


@handle_api_url("admin/request_line")
class ListRequestLine(api.web.APIHandler):
    return_name = "request_line"
    admin_required = True
    sid_required = True

    def post(self):
        self.append(self.return_name, cache.get_station(self.sid, "request_line"))


@handle_api_html_url("request_line")
class ListRequestLineHTML(api.web.PrettyPrintAPIMixin, ListRequestLine):
    pass
