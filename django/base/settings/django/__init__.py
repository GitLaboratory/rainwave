import os

from .general_settings import *
from .log_settings import *

if os.environ.get("RAINWAVE_ENVIRONMENT") == "development":
    from .development_only_settings import *
else:
    from .production_only_settings import *
