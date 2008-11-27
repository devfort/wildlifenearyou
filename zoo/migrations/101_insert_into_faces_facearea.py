from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.InsertRows(
    table_name = 'faces_facearea',
    columns = [u'id', u'name', u'description', u'category_id', u'order', u'is_small'],
    insert_rows = ((33L, u'Hair (top)', u'', 1L, 3L, 0),
 (34L, u'Hair (bottom)', u'', 1L, 2L, 0),
 (35L, u'Lips', u'', 2L, 4L, 1),
 (36L, u'Noses', u'', 2L, 6L, 0),
 (37L, u'Hats', u'', 3L, 10L, 0),
 (38L, u'Cheeks', u'', 2L, 7L, 0),
 (39L, u'Eyes', u'', 2L, 8L, 0),
 (40L, u'Faces', u'', 2L, 1L, 0),
 (41L, u'Glasses', u'', 2L, 9L, 0),
 (42L, u'Beards', u'', 1L, 5L, 0),
 (43L, u'Special Hats', u'', 4L, 11L, 0)),
    delete_ids = [33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]
)
