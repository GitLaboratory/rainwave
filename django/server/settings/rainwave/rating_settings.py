from server.settings.classes import RainwaveRatingMap

# How many ratings until Rainwave will show a public rating on the site?
RW_RATING_CALCULATION_THRESHOLD = 10

# How many ratings until a user is allowed to rate everything freely?
RW_RATING_ALLOW_ALL_THRESHOLD = 1000

# Map user-facing ratings to raw points in the rating formula.
RW_RATING_MAP = [
    RainwaveRatingMap(threshold=0, points=-0.2),
    RainwaveRatingMap(threshold=1.5, points=0),
    RainwaveRatingMap(threshold=2.0, points=0.1),
    RainwaveRatingMap(threshold=2.5, points=0.2),
    RainwaveRatingMap(threshold=3.0, points=0.5),
    RainwaveRatingMap(threshold=3.5, points=0.75),
    RainwaveRatingMap(threshold=4.0, points=0.9),
    RainwaveRatingMap(threshold=4.5, points=1.1),
    RainwaveRatingMap(threshold=5.0, points=1.1),
]
