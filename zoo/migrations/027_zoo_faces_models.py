from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `faces_facearea` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(100) NOT NULL,
        `plural` varchar(100) NOT NULL,
        `shortname` varchar(30) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `faces_facepart` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `area_id` integer NOT NULL,
        `description` varchar(100) NOT NULL,
        `image` varchar(100) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `faces_facepart` ADD CONSTRAINT area_id_refs_id_46909e89 FOREIGN KEY (`area_id`) REFERENCES `faces_facearea` (`id`);
"""], sql_down=["""
    DROP TABLE `faces_facepart`;
""", """
    DROP TABLE `faces_facearea`;
"""])
