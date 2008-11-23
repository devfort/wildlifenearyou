from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `places_country` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(100) NOT NULL,
        `country_code` varchar(2) NOT NULL UNIQUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `places_place` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `legal_name` varchar(500) NOT NULL,
        `known_as` varchar(500) NOT NULL,
        `slug` varchar(255) NOT NULL UNIQUE,
        `created_at` datetime NOT NULL,
        `last_modified_at` datetime NOT NULL,
        `address_line_1` varchar(250) NULL,
        `address_line_2` varchar(250) NULL,
        `town` varchar(250) NULL,
        `state` varchar(250) NULL,
        `zip` varchar(50) NULL,
        `country_id` integer NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
"""], sql_down=["""
    DROP TABLE `places_country`;
""", """
    DROP TABLE `places_place`;
"""])
