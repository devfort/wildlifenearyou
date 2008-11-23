from dmigrations.mysql import migrations as m

class CustomMigration(m.Migration):
    def __init__(self):
        sql_up = ['alter table places_place change column country_id country_id int(11) NOT NULL;']
        sql_down = ['alter table places_place change column country_id country_id int(11) NULL;']
        super(CustomMigration, self).__init__(
            sql_up=sql_up, sql_down=sql_down
        )

migration = CustomMigration()
