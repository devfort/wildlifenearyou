from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime

migration = m.Compound([
    m.AddColumn(
        'animals', 'species', 'needs_indexing', 'bool NOT NULL'
    ),
    m.AddColumn(
        'places', 'place', 'needs_indexing', 'bool NOT NULL'
    ),
    m.AddColumn(
        'accounts', 'profile', 'needs_indexing', 'bool NOT NULL'
    ),
])
