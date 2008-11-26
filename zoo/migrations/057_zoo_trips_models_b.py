from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(
    sql_up   = """ALTER TABLE `trips_trip` DROP COLUMN `place_id`""",
    sql_down = """ALTER TABLE `trips_trip` ADD `place_id` integer NOT NULL REFERENCES `place` (`id`)"""
)
