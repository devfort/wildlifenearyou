from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    DROP TABLE `animals_superspecies`;
""", """
    CREATE TABLE `animals_superspecies` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `common_name` varchar(500) NOT NULL,
        `description` longtext NOT NULL,
        `slug` varchar(255) NOT NULL UNIQUE,
        `species_group_id` integer NULL,
        `type` varchar(10) NOT NULL,
        `latin_name` varchar(500) NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
"""], sql_down=["""
    DROP TABLE `animals_superspecies`;
""", """
    CREATE TABLE `animals_superspecies` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `common_name` varchar(500) NOT NULL,
        `description` longtext NOT NULL,
        `slug` varchar(255) NOT NULL UNIQUE,
        `species_group_id` integer NULL,
        `type` varchar(10) NOT NULL,
        `latin_name` varchar(500) NULL,
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
"""])
# Dirty fake this - the sql_down should recerate the table as it used to be
# but doesn't.