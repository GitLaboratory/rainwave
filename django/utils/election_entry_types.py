class ElectionEntryTypes(object):
    CONFLICT = 0
    WARNING = 1
    NORMAL = 2
    QUEUE = 3
    REQUEST = 4


ELECTION_ENTRY_TYPES_MODEL_CHOICES = [
    (ElectionEntryTypes.CONFLICT, "Conflict"),
    (ElectionEntryTypes.WARNING, "Warning"),
    (ElectionEntryTypes.NORMAL, "Normal"),
    (ElectionEntryTypes.QUEUE, "Queue"),
    (ElectionEntryTypes.REQUEST, "Request"),
]
