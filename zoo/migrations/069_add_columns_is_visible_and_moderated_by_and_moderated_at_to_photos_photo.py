from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Compound([
    m.AddColumn('photos', 'photo', 'is_visible', 'bool NOT NULL'),
    m.AddColumn('photos', 'photo', 'moderated_at', 'datetime NULL'),
    m.AddColumn('photos', 'photo', 'moderated_by', 'integer NULL', 'auth_user'),
])

