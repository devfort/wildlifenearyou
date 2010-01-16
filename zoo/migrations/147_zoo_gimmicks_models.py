from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `gimmicks_gimmick` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `domain` varchar(100) NOT NULL,
        `singlular` varchar(40) NOT NULL,
        `plural` varchar(40) NOT NULL,
        `created` datetime NOT NULL,
        `updated` datetime NOT NULL,
        `custom_template` longtext NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `gimmicks_gimmick_species` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `gimmick_id` integer NOT NULL,
        `species_id` integer NOT NULL,
        UNIQUE (`gimmick_id`, `species_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `gimmicks_gimmick_species` ADD CONSTRAINT `gimmick_id_refs_id_2c161428` FOREIGN KEY (`gimmick_id`) REFERENCES `gimmicks_gimmick` (`id`);
""", """
    ALTER TABLE `gimmicks_gimmick_species` ADD CONSTRAINT `species_id_refs_id_dff38245` FOREIGN KEY (`species_id`) REFERENCES `animals_species` (`id`);
"""], sql_down=["""
    DROP TABLE `gimmicks_gimmick_species`;
""", """
    DROP TABLE `gimmicks_gimmick`;
"""])
