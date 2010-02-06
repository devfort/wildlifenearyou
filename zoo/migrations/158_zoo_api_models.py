from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `api_apikeygroup` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(100) NOT NULL,
        `max_per_day` integer NOT NULL,
        `max_per_hour` integer NOT NULL,
        `max_per_minute` integer NOT NULL,
        `max_per_5_second_burst` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `api_apikey` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `user_id` integer NOT NULL,
        `group_id` integer NOT NULL,
        `key` varchar(20) NOT NULL UNIQUE,
        `purpose` longtext NOT NULL,
        `created_at` datetime NOT NULL,
        `num_calls` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `api_apikey` ADD CONSTRAINT `user_id_refs_id_6ce3a370` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
""", """
    ALTER TABLE `api_apikey` ADD CONSTRAINT `group_id_refs_id_74177057` FOREIGN KEY (`group_id`) REFERENCES `api_apikeygroup` (`id`);
"""], sql_down=["""
    DROP TABLE `api_apikey`;
""", """
    DROP TABLE `api_apikeygroup`;
"""])
