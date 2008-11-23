from dmigrations.mysql import migrations as m
import datetime
migration = m.InsertRows(
    table_name = 'django_site',
    columns = [u'id', u'domain', u'name'],
    insert_rows = ((1L, u'localhost', u'localhost'),),
    delete_ids = [1]
)
