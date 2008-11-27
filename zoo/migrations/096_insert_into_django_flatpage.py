from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.InsertRows(
    table_name = 'django_flatpage',
    columns = [u'id', u'url', u'title', u'content', u'enable_comments', u'template_name', u'registration_required'],
    insert_rows = ((2L, u'/colophon/', u'Colophon', u'', 0, u'flatpages/colophon.html', 0),),
    delete_ids = [2]
)
