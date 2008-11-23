from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.InsertRows(
    table_name = 'django_site',
    columns = [u'id', u'domain', u'name'],
    insert_rows = ((1L, u'localhost', u'localhost'),),
    delete_ids = [1]
)
