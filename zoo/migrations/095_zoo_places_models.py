from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `places_placespecies` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `place_id` integer NOT NULL,
        `species_id` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `places_placespecies` ADD CONSTRAINT species_id_refs_id_3cf88a69 FOREIGN KEY (`species_id`) REFERENCES `animals_species` (`id`);
"""], sql_down=["""
    DROP TABLE `places_placespecies`;
"""])
