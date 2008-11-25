from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m

class CustomMigration(m.Migration):
    def __init__(self):
        sql_up = [
            "UPDATE animals_species SET created_by_id=1, modified_by_id=1",
            "UPDATE animals_speciesgroup SET created_by_id=1, modified_by_id=1",
            "UPDATE places_enclosure SET created_by_id=1, modified_by_id=1",
            "UPDATE places_webcam SET created_by_id=1, modified_by_id=1",
            ]
        sql_down = []
        super(CustomMigration, self).__init__(
            sql_up=sql_up, sql_down=sql_down
        )
    # Or override the up() and down() methods

migration = CustomMigration()
