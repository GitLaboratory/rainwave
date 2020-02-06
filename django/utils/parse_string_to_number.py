from numbers import Number


def parse_string_to_number(s):
    if s is None:
        return None

    if isinstance(s, Number):
        return s

    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return None
