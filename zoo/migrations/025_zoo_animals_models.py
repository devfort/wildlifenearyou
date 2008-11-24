from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    DROP TABLE `animals_animalclass`;
""","""
    DROP TABLE `places_enclosureanimal`;
""","""
    DROP TABLE `animals_animal`;
""","""
    DELETE FROM `places_place`;
""","""
    CREATE TABLE `animals_speciesgroup` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(255) NOT NULL UNIQUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""","""
    CREATE TABLE `animals_species` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `common_name` varchar(500) NOT NULL,
        `latin_name` varchar(500) NOT NULL,
        `slug` varchar(255) NOT NULL UNIQUE,
        `species_group_id` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""","""
    CREATE TABLE `places_enclosurespecies` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `enclosure_id` integer NOT NULL,
        `species_id` integer NOT NULL,
        `number_of_inhabitants` integer NULL,
        `modified_at` datetime NOT NULL,
        `modified_by_id` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""","""
    ALTER TABLE `places_enclosurespecies` ADD CONSTRAINT species_id_refs_id_7d7f4008 FOREIGN KEY (`species_id`) REFERENCES `animals_species` (`id`);
""", """
    ALTER TABLE `places_enclosurespecies` ADD CONSTRAINT modified_by_id_refs_id_5179a31a FOREIGN KEY (`modified_by_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `animals_speciesgroup`;
""","""
    DROP TABLE `places_enclosurespecies`;
""","""
    DROP TABLE `animals_species`;
""","""
    DELETE FROM `places_place`;
""","""
    CREATE TABLE `animals_animalclass` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(255) NOT NULL UNIQUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""","""
    CREATE TABLE `animals_animal` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `common_name` varchar(500) NOT NULL,
        `latin_name` varchar(500) NOT NULL,
        `slug` varchar(255) NOT NULL UNIQUE,
        `animal_class_id` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""","""
    CREATE TABLE `places_enclosureanimal` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `enclosure_id` integer NOT NULL,
        `animal_id` integer NOT NULL,
        `number_of_inhabitants` integer NULL,
        `modified_at` datetime NOT NULL,
        `modified_by_id` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""","""
    ALTER TABLE `places_enclosureanimal` ADD CONSTRAINT animal_id_refs_id_7d7f4008 FOREIGN KEY (`animal_id`) REFERENCES `animals_animal` (`id`);
""", """
    ALTER TABLE `places_enclosureanimal` ADD CONSTRAINT modified_by_id_refs_id_5179a31a FOREIGN KEY (`modified_by_id`) REFERENCES `auth_user` (`id`);
"""])
