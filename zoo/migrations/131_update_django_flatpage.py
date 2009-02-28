from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    UPDATE `django_flatpage` SET url='/legal/', title='Legal statement', template_name='flatpages/legal.html' WHERE id=2;"""],sql_down=["""
    UPDATE `django_flatpage` SET url='/colophon/', title='Colophon', template_name='flatpages/colophon.html' WHERE id=2;"""]
)
