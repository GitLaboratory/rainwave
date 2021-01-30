class TemplateBind:
    name: str
    ts_type: str
    uid: str
    inside_if: bool

    def __init__(self, name, ts_type, uid):
        self.name = name
        self.ts_type = ts_type
        self.uid = uid
        self.inside_if = False
