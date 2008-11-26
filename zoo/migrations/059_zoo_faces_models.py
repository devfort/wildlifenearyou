from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `faces_selectedfacepart` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `part_id` integer NOT NULL,
        `area_id` integer NOT NULL,
        `user_id` integer NOT NULL,
        UNIQUE (`area_id`, `user_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `faces_selectedfacepart` ADD CONSTRAINT user_id_refs_id_3f3cdb3c FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `faces_selectedfacepart`;
"""])
