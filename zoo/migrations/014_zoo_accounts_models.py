from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `accounts_profile` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `user_id` integer NOT NULL UNIQUE,
        `user_level_id` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `accounts_profile` ADD CONSTRAINT user_id_refs_id_46e869e2 FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `accounts_profile`;
"""])
