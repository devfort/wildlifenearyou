from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Compound([
    m.AddColumn('trips', 'trip', 'created_at', 'datetime NOT NULL'),
    m.AddColumn('trips', 'trip', 'modified_at', 'datetime NOT NULL'),
    m.AddColumn('trips', 'trip', 'created_by', 'integer NOT NULL', 'auth_user'),
    m.AddColumn('trips', 'trip', 'modified_by', 'integer NOT NULL', 'auth_user'),
])

