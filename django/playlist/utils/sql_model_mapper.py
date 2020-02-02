from typing import Set, Dict
from django.db import connection


class SQLModelMapper:
    # we can't set these to null or pylint complains :|
    _models:set = ()
    _column_to_vars: Dict[str, Set[str]] = {}

    @classmethod
    def _solve_table_to_vars(cls):
        if not cls._column_to_vars:
            # this needs to be set to something new or all classes share the same dict
            # because of pylint's complaining above.
            cls._column_to_vars = {}
            for (model, model_instance_attribute) in cls._models:
                for field in model._meta.concrete_fields:
                    field_column = field.db_column or field.name
                    cls._column_to_vars.setdefault(field_column, set())
                    cls._column_to_vars[field_column].add(
                        (model_instance_attribute, field.name)
                    )

    @classmethod
    def iterate(cls, query, params=None):
        cls._solve_table_to_vars()
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            column_names = [column[0] for column in cursor.description]
            raw_row = cursor.fetchone()
            while raw_row:
                instance = cls()
                for index, value in enumerate(raw_row):
                    for (
                        model_instance_attribute,
                        field_name,
                    ) in cls._column_to_vars.get(column_names[index], []):
                        setattr(
                            getattr(instance, model_instance_attribute),
                            field_name,
                            value,
                        )
                yield instance
                raw_row = cursor.fetchone()

    def __init__(self):
        for (model, attribute) in self._models:
            setattr(self, attribute, model())
