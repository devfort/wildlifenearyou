from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.InsertRows(
    table_name = 'places_placecategory',
    columns = [u'id', u'name', u'slug', u'order'],
    insert_rows = ((1L, u'Zoo', u'zoo', None),
 (2L, u'Aquarium', u'aquarium', None),
 (3L, u'Petting zoo', u'petting-zoo', None),
 (4L, u'Rescue centre', u'rescue-centre', None),
 (5L, u'City park', u'city-park', None),
 (6L, u'National park', u'national-park', None),
 (7L, u'Farm', u'farm', None),
 (8L, u'Nature reserve', u'nature-reserve', None),
 (9L, u'Safari park', u'safari-park', None),
 (10L, u'Forest or Wood', u'forest', None),
 (11L, u'Beach or coast', u'coast', None),
 (12L, u'Mountain', u'mountain', None)),
    delete_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
)
