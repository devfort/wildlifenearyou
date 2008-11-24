from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `trips_tripsighting` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `trip_id` integer NOT NULL,
        `species_id` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `trips_tripsighting` ADD CONSTRAINT species_id_refs_id_56a11b3f FOREIGN KEY (`species_id`) REFERENCES `animals_species` (`id`);
"""], sql_down=["""
    DROP TABLE `trips_tripsighting`;
"""])
