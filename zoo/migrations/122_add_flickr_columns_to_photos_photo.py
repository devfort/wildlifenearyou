from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
migration = m.Compound([
    m.AddColumn('photos', 'photo', 'flickr_id', 'varchar(32) NOT NULL'),
    m.AddColumn('photos', 'photo', 'flickr_secret', 'varchar(32) NOT NULL'),
    m.AddColumn('photos', 'photo', 'flickr_server', 'varchar(16) NOT NULL')
])
