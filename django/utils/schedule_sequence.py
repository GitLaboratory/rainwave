from django.db import connection, models


def next_schedule_sequence_id():
    with connection.cursor() as cursor:
        cursor.execute("SELECT nextval('r4_schedule_sched_id_seq')")
        return cursor.fetchone()[0]
