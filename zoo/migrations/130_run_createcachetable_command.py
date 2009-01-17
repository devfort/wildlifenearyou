"""
A very cheeky command - doesn't modify the database in a traditional sense
at all, just makes sure that ./manage.py createcachetable has been called
and silently supresses errors in the case that it has already been created.
"""

from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m

from django.core.management import call_command

class CustomMigration(m.Migration):
    def __init__(self):
        super(CustomMigration, self).__init__(
            sql_up=[], sql_down=[]
        )
        def up(self):
            try:
                call_command('createcachetable', 'django_cache')
            except:
                pass
        
        def down(self):
            pass

migration = CustomMigration()
