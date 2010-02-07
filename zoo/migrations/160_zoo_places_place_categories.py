from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `places_placecategory` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(100) NOT NULL,
        `slug` varchar(50) NOT NULL UNIQUE,
        `order` integer
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `places_place_categories` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `place_id` integer NOT NULL,
        `placecategory_id` integer NOT NULL,
        UNIQUE (`place_id`, `placecategory_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `places_place_categories` ADD CONSTRAINT `place_id_refs_id_83fdc427` FOREIGN KEY (`place_id`) REFERENCES `places_place` (`id`);
""", """
    ALTER TABLE `places_place_categories` ADD CONSTRAINT `placecategory_id_refs_id_f0baac59` FOREIGN KEY (`placecategory_id`) REFERENCES `places_placecategory` (`id`);
"""], sql_down=["""
    DROP TABLE `places_place_categories`;
""", """
    DROP TABLE `places_placecategory`;
"""])
