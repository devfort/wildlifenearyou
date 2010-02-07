from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Compound([
    m.AddColumn('places', 'place', 'is_unlisted', 'bool NOT NULL'),
    m.AddColumn('places', 'place', 'is_temporary', 'bool NOT NULL'),
])

