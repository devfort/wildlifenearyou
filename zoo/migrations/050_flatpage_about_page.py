from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m

class CustomMigration(m.Migration):
    def __init__(self):
        sql_up = [
'''insert into django_flatpage_sites values (1,1,1)''',
'''insert into django_flatpage values (1, '/about/', 'About', '', 0, 'flatpages/about.html', 0)''',
]
        sql_down = [
'''delete from django_flatpage_sites where flatpage_id=1''',
'''delete from django_flatpage where id=1''',
]
        super(CustomMigration, self).__init__(
            sql_up=sql_up, sql_down=sql_down
        )
    # Or override the up() and down() methods

migration = CustomMigration()
