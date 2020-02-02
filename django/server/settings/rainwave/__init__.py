import os

from .cooldown_settings import *
from .general_settings import *
from .history_settings import *
from .memcache_settings import *
from .rating_settings import *
from .relay_settings import *
from .scanner_settings import *
from .station_settings import *
from .url_settings import *

if os.environ.get("RAINWAVE_ENVIRONMENT") == "development":
    from .rw_development_only_settings import *
else:
    from .rw_production_only_settings import *
