Needs to be done on the server before implementing Django:

On production DBs:
ALTER TABLE phpbb_users ADD is_staff BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE phpbb_users ADD is_superuser BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE phpbb_users ADD is_active BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE r4_album_sid ADD album_sid_id SERIAL;
CREATE INDEX r4_album_sid_id ON r4_album_sid (album_sid_id);

On test DBs:
(phpbb shit to come soon)
