from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m

migration = m.Compound([
    m.AddColumn('places', 'place', 'freebase_id', 'varchar(100) NOT NULL'),
    m.AddColumn('places', 'place', 'wikipedia_url', 'varchar(255) NOT NULL'),
])
