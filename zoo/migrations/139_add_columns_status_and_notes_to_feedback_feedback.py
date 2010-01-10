from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Compound([
    m.AddColumn('feedback', 'feedback', 'status', 'varchar(100)'),
    m.AddColumn('feedback', 'feedback', 'notes', 'longtext'),
])

