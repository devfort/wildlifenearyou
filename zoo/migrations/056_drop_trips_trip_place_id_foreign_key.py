from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m

class CustomMigration(m.Migration):
    def __init__(self):
        sql_up = """ALTER TABLE `trips_trip` DROP FOREIGN KEY place_id_refs_id_2ede8a1"""
        sql_down = """ALTER TABLE `trips_trip` ADD CONSTRAINT place_id_refs_id_2ede8a1 FOREIGN KEY (`place_id`) REFERENCES `places_place` (`id`)"""
        super(CustomMigration, self).__init__(
            sql_up=sql_up, sql_down=sql_down
        )
    # Or override the up() and down() methods

migration = CustomMigration()
