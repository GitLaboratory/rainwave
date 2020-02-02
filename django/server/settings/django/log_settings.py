import logging

# PIL, the imaging library, starts using logging before Django can finish setting it up.
# It leads to a bunch of pointless debug messages about which image libraries its loading
# every startup, which is very annoying when running tests or restarting the server.
pil_logger = logging.getLogger("PIL.Image")
pil_logger.setLevel(logging.INFO)


class RainwaveLogFormatter(logging.Formatter):
    MAX_MODULE_LENGTH = 30
    MAX_LEVEL_LENGTH = 8

    def __init__(self, fmt=None, datefmt=None, style="%"):
        fmt = f"[%(name)-{self.MAX_MODULE_LENGTH}s] [%(levelname)-{self.MAX_LEVEL_LENGTH}s] %(message)s"
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        if len(record.name) > self.MAX_MODULE_LENGTH:
            record.name = "..." + record.name[-(self.MAX_MODULE_LENGTH - 3) :]
        msg = super().format(record)
        msg = msg.replace(
            "\n",
            "\n"
            + " " * (self.MAX_MODULE_LENGTH + 2 + 1 + self.MAX_LEVEL_LENGTH + 2 + 1),
        )
        return msg


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"verbose": {"()": RainwaveLogFormatter}},
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        "null": {"class": "logging.NullHandler", "formatter": "verbose"},
    },
    "loggers": {
        "": {"handlers": ["console"], "level": "DEBUG"},
        "django": {"formatter": "verbose"},
    },
}

# These log modules produce a lot of 3rd party or excess
# spam that gets in the way of useful debug output while developing.
IGNORED_LOG_MODULES = [
    "api.views",
    "application",
    "django.server",
    "PIL",
    "urllib3",
    "asyncio",
    "parso",
]

for ignored_module in IGNORED_LOG_MODULES:
    LOGGING["loggers"][ignored_module] = {"level": "ERROR"}
