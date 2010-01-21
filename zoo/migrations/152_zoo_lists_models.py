from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `lists_list` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `created_at` datetime NOT NULL,
        `created_by_id` integer NOT NULL,
        `modified_at` datetime NOT NULL,
        `modified_by_id` integer NOT NULL,
        `title` varchar(255) NOT NULL,
        `slug` varchar(50) NOT NULL,
        `description` longtext NOT NULL,
        `source_url` varchar(255) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `lists_list` ADD CONSTRAINT `created_by_id_refs_id_8674b840` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
""", """
    ALTER TABLE `lists_list` ADD CONSTRAINT `modified_by_id_refs_id_8674b840` FOREIGN KEY (`modified_by_id`) REFERENCES `auth_user` (`id`);
""", """
    CREATE TABLE `lists_list_species` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `list_id` integer NOT NULL,
        `species_id` integer NOT NULL,
        UNIQUE (`list_id`, `species_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `lists_list_species` ADD CONSTRAINT `list_id_refs_id_34cfa79c` FOREIGN KEY (`list_id`) REFERENCES `lists_list` (`id`);
""", """
    ALTER TABLE `lists_list_species` ADD CONSTRAINT `species_id_refs_id_73a26573` FOREIGN KEY (`species_id`) REFERENCES `animals_species` (`id`);
""", """
    CREATE TABLE `lists_list_places` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `list_id` integer NOT NULL,
        `place_id` integer NOT NULL,
        UNIQUE (`list_id`, `place_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `lists_list_places` ADD CONSTRAINT `list_id_refs_id_6395c115` FOREIGN KEY (`list_id`) REFERENCES `lists_list` (`id`);
""", """
    ALTER TABLE `lists_list_places` ADD CONSTRAINT `place_id_refs_id_b7d2a24d` FOREIGN KEY (`place_id`) REFERENCES `places_place` (`id`);
"""], sql_down=["""
    DROP TABLE `lists_list_places`;
""", """
    DROP TABLE `lists_list_species`;
""", """
    DROP TABLE `lists_list`;
"""])
