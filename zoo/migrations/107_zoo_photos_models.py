from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    DROP TABLE `photos_photo_contained_species`;
"""], sql_down=["""
    CREATE TABLE `photos_photo_contained_species` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `photo_id` integer NOT NULL,
        `species_id` integer NOT NULL,
        UNIQUE (`photo_id`, `species_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `photos_photo_contained_species` ADD CONSTRAINT photo_id_refs_id_38fa3104 FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`);
""", """
    ALTER TABLE `photos_photo_contained_species` ADD CONSTRAINT species_id_refs_id_13bab37 FOREIGN KEY (`species_id`) REFERENCES `animals_species` (`id`);
"""])
