from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `rspb_rspbbirdpage` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(255) NOT NULL,
        `species_id` integer,
        `url` varchar(255) NOT NULL,
        `image_url` varchar(255) NOT NULL,
        `teaser` longtext NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `rspb_rspbbirdpage` ADD CONSTRAINT `species_id_refs_id_a230c37a` FOREIGN KEY (`species_id`) REFERENCES `animals_species` (`id`);
"""], sql_down=["""
    DROP TABLE `rspb_rspbbirdpage`;
"""])
