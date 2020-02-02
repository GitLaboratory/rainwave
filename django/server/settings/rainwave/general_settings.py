# Will the /beta URL be available to the public (true), or only select groups (false)?
RW_PUBLIC_BETA = True

# Set to store PID files for service usage
RW_PID_DIR = None

# If you need to run WebSockets on a different host because of
# any sort of CDN, enter a host here.
# If you're not using a CDN, leave as null.
# An example would be 'websockets.mydomain.com'
RW_WEBSOCKET_HOST = None

# What domains/IP addresses should WebSocket connections be allowed from?
# Set to * to allow from anywhere.
RW_WEBSOCKET_ALLOW_FROM = "127.0.0.1,::1"

# Set to true if using LiquidSoap.
RW_USE_LIQUIDSOAP_ANNOTATIONS = False

# Copy value from your phpBB install, or leave alone for testing/no phpBB.
RW_PHPBB_COOKIE_NAME = "phpbb3_"

# Make the front page require a login.  It's not elegant - it will throw an error at users.
RW_INDEX_REQUIRES_LOGIN = False

# Accept automated Javascript error reports from these hosts. (spam prevention)
# Individual station hosts are automatically included.
RW_ACCEPT_ERROR_REPORTS_FROM_HOSTS = ["localhost"]
