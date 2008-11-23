from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `animals_animalclass` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(500) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
    CREATE TABLE `animals_animal` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `common_name` varchar(500) NOT NULL,
        `latin_name` varchar(500) NOT NULL,
        `animal_class_id` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;

"""], sql_down=["""
    DROP TABLE `animals_animalclass`;
    DROP TABLE `animals_animal`;
"""])
