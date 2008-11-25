from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m

class CustomMigration(m.Migration):
    def __init__(self):
        sql_up = ["""
UPDATE `animals_superspecies` SET latin_name = 'raphus cucullatus' WHERE id = '1'
""","""
UPDATE `animals_superspecies` SET latin_name = 'mammuthus primigenius' WHERE id = '2'
""","""
UPDATE `animals_superspecies` SET latin_name = 'equus unicornis' WHERE id = '3'
""","""
UPDATE `animals_superspecies` SET latin_name = 'homo lycanthropus' WHERE id = '4'
""","""
UPDATE `animals_superspecies` SET latin_name = 'draco draco' WHERE id = '5'
""","""
UPDATE `animals_superspecies` SET latin_name = 'chimaera chimaera' WHERE id = '6'
""","""
UPDATE `animals_superspecies` SET latin_name = 'gryphus' WHERE id = '7'
""","""
UPDATE `animals_superspecies` SET latin_name = 'monodon monocerosusess' WHERE id = '8'
"""]
        sql_down = [
"DELETE FROM `animals_superspecies`"
]
        super(CustomMigration, self).__init__(
            sql_up=sql_up, sql_down=sql_down
        )
    # Or override the up() and down() methods

migration = CustomMigration()
