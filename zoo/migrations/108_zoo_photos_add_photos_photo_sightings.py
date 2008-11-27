from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `photos_photo_sightings` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `photo_id` integer NOT NULL,
        `sighting_id` integer NOT NULL,
        UNIQUE (`photo_id`, `sighting_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `photos_photo_sightings` ADD CONSTRAINT photo_id_refs_id_75a60450 FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`);
""", """
    ALTER TABLE `photos_photo_sightings` ADD CONSTRAINT sighting_id_refs_id_abf3522 FOREIGN KEY (`sighting_id`) REFERENCES `trips_sighting` (`id`);
"""], sql_down=["""
    DROP TABLE `photos_photo_sightings` CASCADE;
"""])
