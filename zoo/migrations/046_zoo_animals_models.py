from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `animals_superspecies` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `created_at` datetime NOT NULL,
        `created_by_id` integer NOT NULL,
        `modified_at` datetime NOT NULL,
        `modified_by_id` integer NOT NULL,
        `common_name` varchar(500) NOT NULL,
        `slug` varchar(255) NOT NULL UNIQUE,
        `type` varchar(10) NOT NULL,
        `latin_name` varchar(500) NULL,
        `species_group_id` integer NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `animals_superspecies` ADD CONSTRAINT created_by_id_refs_id_5a9fbc3b FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
""", """
    ALTER TABLE `animals_superspecies` ADD CONSTRAINT modified_by_id_refs_id_5a9fbc3b FOREIGN KEY (`modified_by_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `animals_superspecies`;
"""])
