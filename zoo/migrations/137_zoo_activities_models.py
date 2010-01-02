from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `activities_event` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `created` datetime NOT NULL,
        `type` varchar(50) NOT NULL,
        `description` longtext NOT NULL,
        `user_id` integer,
        `custom_1` varchar(255) NOT NULL,
        `custom_2` varchar(255) NOT NULL,
        `custom_3` varchar(255) NOT NULL,
        `url` varchar(255) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `activities_event` ADD CONSTRAINT `user_id_refs_id_fae96f6` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `activities_event`;
"""])
