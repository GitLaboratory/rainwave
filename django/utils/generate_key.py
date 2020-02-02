import random
import string


def generate_key():
    return "".join(
        random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)
        for x in range(10)
    )
