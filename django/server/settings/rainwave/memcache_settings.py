# Use a fake memcache server in local memory.  Use for corner-case debugging.
RW_MEMCACHE_FAKE = False

RW_MEMCACHE_SERVERS = ["127.0.0.1"]
RW_MEMCACHE_KETAMA = False

# It's recommended to use a separate cache for ratings in production.
# The ratings cache is extremely volatile and can churn the main cache.
RW_MEMCACHE_RATINGS_SERVERS = ["127.0.0.1"]
RW_MEMCACHE_RATINGS_KETAMA = False
