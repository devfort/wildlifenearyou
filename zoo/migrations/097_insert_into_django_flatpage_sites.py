from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.InsertRows(
    table_name = 'django_flatpage_sites',
    columns = [u'id', u'flatpage_id', u'site_id'],
    insert_rows = ((2L, 2L, 1L),),
    delete_ids = [2]
)
