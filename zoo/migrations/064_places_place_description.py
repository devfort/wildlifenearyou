from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime

migration = m.AddColumn('places', 'place', 'description', 'longtext NOT NULL default ""')
migration = m.AddColumn('places', 'place', 'url', 'varchar(200) NOT NULL default ""')

