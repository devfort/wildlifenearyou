from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `linkeddata_wikipediaabstract` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `species_id` integer NOT NULL,
        `abstract` longtext NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `linkeddata_wikipediaabstract` ADD CONSTRAINT `species_id_refs_id_cd970c85` FOREIGN KEY (`species_id`) REFERENCES `animals_species` (`id`);
"""], sql_down=["""
    DROP TABLE `linkeddata_wikipediaabstract`;
"""])
