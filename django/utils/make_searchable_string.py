from unidecode import unidecode


def make_searchable_string(s):
    if not isinstance(s, str):
        s = str(s)
    s = unidecode(s).lower()
    return "".join(e for e in s if (e.isalnum() or e == " "))
