RW_ENFORCE_HSTS = False
RW_EXTERNAL_HOSTNAME = "localhost"

if RW_ENFORCE_HSTS:
    RW_EXTERNAL_BASE_SITE_URL = f"http://{RW_EXTERNAL_HOSTNAME}"
else:
    RW_EXTERNAL_BASE_SITE_URL = f"https://{RW_EXTERNAL_HOSTNAME}"

RW_API_BASE_PORT = 20000

# What does the API address look like for end-user browsers?
RW_API_EXTERNAL_URL_PREFIX = "//localhost:20000/api4/"
