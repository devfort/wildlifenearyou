from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `itis_kingdom` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(50) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `itis_rank` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(50) NOT NULL,
        `kingdom_id` integer NOT NULL,
        `itis_id` integer NOT NULL,
        `dir_parent_rank_id` integer,
        `req_parent_rank_id` integer
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `itis_rank` ADD CONSTRAINT `kingdom_id_refs_id_5416cba5` FOREIGN KEY (`kingdom_id`) REFERENCES `itis_kingdom` (`id`);
""", """
    ALTER TABLE `itis_rank` ADD CONSTRAINT `dir_parent_rank_id_refs_id_c1557c93` FOREIGN KEY (`dir_parent_rank_id`) REFERENCES `itis_rank` (`id`);
""", """
    ALTER TABLE `itis_rank` ADD CONSTRAINT `req_parent_rank_id_refs_id_c1557c93` FOREIGN KEY (`req_parent_rank_id`) REFERENCES `itis_rank` (`id`);
""", """
    CREATE TABLE `itis_species` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name1` varchar(100) NOT NULL,
        `name2` varchar(100) NOT NULL,
        `name3` varchar(100) NOT NULL,
        `name4` varchar(100) NOT NULL,
        `parent_id` integer,
        `rank_id` integer NOT NULL,
        `kingdom_id` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `itis_species` ADD CONSTRAINT `rank_id_refs_id_ec29df00` FOREIGN KEY (`rank_id`) REFERENCES `itis_rank` (`id`);
""", """
    ALTER TABLE `itis_species` ADD CONSTRAINT `kingdom_id_refs_id_216d2738` FOREIGN KEY (`kingdom_id`) REFERENCES `itis_kingdom` (`id`);
""", """
    ALTER TABLE `itis_species` ADD CONSTRAINT `parent_id_refs_id_1886b0ed` FOREIGN KEY (`parent_id`) REFERENCES `itis_species` (`id`);
""", """
    CREATE TABLE `itis_vernaculars` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(255) NOT NULL,
        `language` varchar(30) NOT NULL,
        `is_approved` bool NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
"""], sql_down=["""
    DROP TABLE `itis_vernaculars`;
""", """
    ALTER TABLE `itis_species` DROP FOREIGN KEY parent_id_refs_id_1886b0ed;
""", """
    DROP TABLE `itis_species`;
""", """
    ALTER TABLE `itis_rank` DROP FOREIGN KEY req_parent_rank_id_refs_id_c1557c93;
""", """
    ALTER TABLE `itis_rank` DROP FOREIGN KEY dir_parent_rank_id_refs_id_c1557c93;
""", """
    DROP TABLE `itis_rank`;
""", """
    DROP TABLE `itis_kingdom`;
"""])
