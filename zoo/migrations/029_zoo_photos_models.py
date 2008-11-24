from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `photos_photo` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `created_by_id` integer NOT NULL,
        `created_at` datetime NOT NULL,
        `title` varchar(255) NOT NULL,
        `photo` varchar(100) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `photos_photo` ADD CONSTRAINT created_by_id_refs_id_5d63593a FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `photos_photo`;
"""])
