from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.InsertRows(
    table_name = 'faces_faceareacategory',
    columns = [u'id', u'name', u'is_special', u'`order`'],
    insert_rows = ((1L, u'Hair', 0, 2L),
 (2L, u'Face', 0, 1L),
 (3L, u'Accessories', 0, 3L),
 (4L, u'Staff only', 1, 4L)),
    delete_ids = [1, 2, 3, 4]
)
