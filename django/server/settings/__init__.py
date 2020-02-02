from .django import *
from .rainwave import *

try:
    from .local_settings import *
except ImportError:
    pass

RW_STATIONS_BY_ID = {station.station_id: station for station in RW_STATIONS}
