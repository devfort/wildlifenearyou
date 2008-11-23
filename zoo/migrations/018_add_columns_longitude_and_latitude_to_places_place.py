from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Compound([
    m.AddColumn('places', 'place', 'longitude', 'double precision NULL'),
    m.AddColumn('places', 'place', 'latitude', 'double precision NULL'),
])

