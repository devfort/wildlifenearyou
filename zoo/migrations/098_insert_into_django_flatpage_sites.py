from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
m1 = m.InsertRows(
    table_name = 'django_flatpage',
    columns = [u'id', u'url', u'title', u'content', u'enable_comments', u'template_name', u'registration_required'],
    insert_rows = ((3L, u'/contact_us/', u'Contact us', u'', 0, u'flatpages/contact_us.html', 0),),
    delete_ids = [3]
)
m2 = m.InsertRows(
    table_name = 'django_flatpage_sites',
    columns = [u'id', u'flatpage_id', u'site_id'],
    insert_rows = ((3L, 3L, 1L),),
    delete_ids = [3]
)

migration = m.Compound([m1, m2])
