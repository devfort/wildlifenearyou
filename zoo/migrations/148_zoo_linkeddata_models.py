from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `linkeddata_externalidentifier` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `species_id` integer NOT NULL,
        `source` varchar(255) NOT NULL,
        `namespace` varchar(255) NOT NULL,
        `key` varchar(255) NOT NULL,
        `uri` varchar(255) NOT NULL,
        `order` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `linkeddata_externalidentifier` ADD CONSTRAINT `species_id_refs_id_4b83c851` FOREIGN KEY (`species_id`) REFERENCES `animals_species` (`id`);
"""], sql_down=["""
    DROP TABLE `linkeddata_externalidentifier`;
"""])
