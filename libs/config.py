try:
    import ujson as json
except ImportError:
    import json
import os
import getpass
import tempfile

# Options hash - please don't access this externally in case the storage method changes
_opts = {}
build_number = 0

# This is used as a global flag.  Modules that require slightly different functionality
# under test purposes (e.g. bypass song verification) will look here to see if we're
# running unit tests.
test_mode = False

station_ids = set()
station_id_friendly = {}
station_hostnames = {}
public_relays = None
public_relays_json = {}
station_list = {}
station_list_json = {}
station_mounts = {}
station_mount_filenames = {}
stream_filename_to_sid = {}
csp_header = ""


def get_build_number():
    bnf = open(os.path.join(os.path.dirname(__file__), "../etc/buildnum"), "r")
    bn = int(bnf.read())
    bnf.close()
    return bn


def get_config_file(testmode=False):
    if os.path.isfile("etc/%s.conf" % getpass.getuser()):
        return "etc/%s.conf" % getpass.getuser()
    elif testmode and os.path.isfile("etc/rainwave_test.conf"):
        return "etc/rainwave_test.conf"
    elif os.path.isfile("etc/rainwave.conf"):
        return "etc/rainwave.conf"
    elif os.path.isfile("/etc/rainwave.conf"):
        return "/etc/rainwave.conf"
    elif testmode:
        raise RuntimeError(
            "Could not find a configuration file at etc/rainwave_test.conf."
        )
    else:
        raise RuntimeError(
            "Could not find a configuration file at etc/rainwave.conf or /etc/rainwave.conf"
        )


def load(filename=None, testmode=False):
    global _opts
    global test_mode
    global build_number
    global public_relays
    global public_relays_json
    global station_ids
    global station_list
    global station_list_json
    global station_hostnames
    global station_mount_filenames

    if not filename:
        filename = get_config_file(testmode)

    config_file = open(filename)
    _opts = json.load(config_file)
    config_file.close()

    stations = _opts.pop("stations")
    _opts["stations"] = {}
    for key in list(stations.keys()):
        _opts["stations"][int(key)] = stations[key]

    require("stations")
    set_station_ids(get("song_dirs"), get("station_id_friendly"))
    if get("test_mode") == True:
        test_mode = True

    public_relays = {}
    relay_hostnames = []
    for sid in station_ids:
        public_relays[sid] = []
        public_relays[sid].append(
            {
                "name": "Random",
                "protocol": "http://",
                "hostname": get_station(sid, "round_robin_relay_host"),
                "port": get_station(sid, "round_robin_relay_port"),
            }
        )
        relay_hostnames.append(
            "http://{}".format(get_station(sid, "round_robin_relay_host"))
        )
        for relay_name, relay in get("relays").items():
            if sid in relay["sids"]:
                public_relays[sid].append(
                    {
                        "name": relay_name,
                        "protocol": relay["protocol"],
                        "hostname": relay["hostname"],
                        "port": relay["port"],
                    }
                )
                relay_hostname = relay["protocol"] + relay["hostname"]
                if not relay_hostname in relay_hostnames:
                    relay_hostnames.append(relay_hostname)
                relay_hostname_port = "{}{}:{}".format(
                    relay["protocol"], relay["hostname"], relay["port"]
                )
                if not relay_hostname_port in relay_hostnames:
                    relay_hostnames.append(relay_hostname_port)
        public_relays_json[sid] = json.dumps(public_relays[sid])
        station_hostnames[get_station(sid, "host")] = sid
        station_mount_filenames[sid] = get_station(sid, "stream_filename")
        stream_filename_to_sid[get_station(sid, "stream_filename")] = sid

    global csp_header
    csp_header = ";".join(
        [
            "default-src 'self' *.{} https://www.google.com https://calendar.google.com".format(
                get("hostname")
            ),
            "object-src 'none'",
            "media-src {}".format(" ".join(relay_hostnames)),
            "font-src 'self' data: https://fonts.googleapis.com https://fonts.gstatic.com/",
            "connect-src wss://websocket.rainwave.cc",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
        ]
    )

    station_list = {}
    for station_id in station_ids:
        station_list[station_id] = {
            "id": station_id,
            "name": station_id_friendly[station_id],
            "url": "{}{}/".format(
                get("base_site_url"), station_mount_filenames[station_id]
            ),
        }
        station_mounts[get_station(station_id, "stream_filename") + ".mp3"] = station_id
        station_mounts[get_station(station_id, "stream_filename") + ".ogg"] = station_id
    station_list_json = json.dumps(station_list, ensure_ascii=False)

    build_number = get_build_number()


def has(key):
    return key in _opts


def has_station(sid, key):
    if not sid in _opts["stations"]:
        return False
    if not key in _opts["stations"][sid]:
        return False
    return True


def require(key):
    if not key in _opts:
        raise Exception("Required configuration key '%s' not found." % key)


def get(key):
    require(key)
    return _opts[key]


def get_directory(key):
    value = get(key)
    if not value:
        return tempfile.gettempdir()
    return value


def set_value(key, value):
    _opts[key] = value
    return value


def override(key, value):
    _opts[key] = value


def get_station(sid, key):
    if not sid in _opts["stations"]:
        raise Exception("Station SID %s has no configuration." % sid)
    if not key in _opts["stations"][sid]:
        raise Exception("Station SID %s has no configuration key %s." % (sid, key))
    return _opts["stations"][sid][key]


def set_station_ids(dirs, friendly):
    global station_ids
    global station_id_friendly

    sid_array = []
    for d, sids in dirs.items():  # pylint: disable=W0612
        for sid in sids:
            if sid_array.count(sid) == 0 and sid != 0:
                sid_array.append(sid)
    station_ids = set(sid_array)

    for sid, friendly in friendly.items():
        station_id_friendly[int(sid)] = friendly
