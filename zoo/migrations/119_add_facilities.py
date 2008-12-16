from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.InsertRows(
    table_name = 'places_facility',
    columns = [u'id', u'icon', u'default_desc'],
    insert_rows = (
    (1L,
    u'facility_icons/cafe.png',
    u'Cafe',
    ),
    (2L,
    u'facility_icons/dining.png',
    u'Dining',
    ),
    (3L,
    u'facility_icons/firstaid.png',
    u'First aid',
    ),
    (4L,
    u'facility_icons/giftshop.png',
    u'Gift shop',
    ),
    (5L,
    u'facility_icons/handicapped.png',
    u'Disabled support',
    ),
    (6L,
    u'facility_icons/information.png',
    u'Information',
    ),
    (7L,
    u'facility_icons/nosmoking.png',
    u'No smoking',
    ),
    (8L,
    u'facility_icons/parking.png',
    u'Parking',
    ),
    (9L,
    u'facility_icons/phone.png',
    u'Phone',
    ),
    ),
    delete_ids = [1,2,3,4,5,6,7,8,9]
)
