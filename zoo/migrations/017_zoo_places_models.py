from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `places_enclosureanimal` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `enclosure_id` integer NOT NULL,
        `animal_id` integer NOT NULL,
        `number_of_inhabitants` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `places_enclosureanimal` ADD CONSTRAINT animal_id_refs_id_7ec919dc FOREIGN KEY (`animal_id`) REFERENCES `animals_animal` (`id`);
"""], sql_down=["""
    DROP TABLE `places_enclosureanimal`;
"""])
