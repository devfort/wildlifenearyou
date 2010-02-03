from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Compound([
    m.AddColumn('accounts', 'profile', 'flickr_token', 'varchar(255)'),
    m.AddColumn('accounts', 'profile', 'flickr_prefs_set_at', 'datetime'),
    m.AddColumn('accounts', 'profile', 'flickr_tag_common_names', 'bool'),
    m.AddColumn('accounts', 'profile', 'flickr_tag_scientific_names', 'bool'),
    m.AddColumn('accounts', 'profile', 'flickr_geotag', 'bool'),
])

