from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
m1 = m.AddColumn('places', 'place', 'featured', 'bool NOT NULL')
m2 = m.AddColumn('animals', 'species', 'featured', 'bool NOT NULL')
m3 = m.AddColumn('accounts', 'profile', 'featured', 'bool NOT NULL')

migration = m.Compound([m1, m2, m3])
