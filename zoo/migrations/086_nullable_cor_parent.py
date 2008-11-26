from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m

class CustomMigration(m.Migration):
    def __init__(self):
        sql_up = ['alter table changerequests_createobjectrequest change column parent_id parent_id integer NULL;']
        sql_down = ['alter table changerequests_createobjectrequest change column parent_id parent_id integer NOT NULL;']

        super(CustomMigration, self).__init__(
            sql_up=sql_up, sql_down=sql_down
        )

migration = CustomMigration()
