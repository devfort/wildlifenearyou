from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.InsertRows(
    table_name = 'geonames_geoname',
    columns = [u'id', u'country_code', u'postal_code', u'place_name', u'admin_name1', u'admin_code1', u'admin_name2', u'admin_code2', u'admin_name3', u'latitude', u'longitude', u'accuracy'],
    insert_rows = (),
    delete_ids = [],
)

