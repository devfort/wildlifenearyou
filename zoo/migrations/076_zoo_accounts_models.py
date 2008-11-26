from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `accounts_badge` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(100) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
    ""","""
    CREATE TABLE `accounts_profilebadge` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `created_at` datetime NOT NULL,
        `created_by_id` integer NOT NULL,
        `modified_at` datetime NOT NULL,
        `modified_by_id` integer NOT NULL,
        `profile_id` integer NOT NULL,
        `badge_id` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
    """, """
        ALTER TABLE `accounts_profilebadge` ADD CONSTRAINT created_by_id_refs_id_608b1682 FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
    """, """
        ALTER TABLE `accounts_profilebadge` ADD CONSTRAINT modified_by_id_refs_id_608b1682 FOREIGN KEY (`modified_by_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `accounts_badge`;
    ""","""
    DROP TABLE `accounts_profilebadge`;
"""])
