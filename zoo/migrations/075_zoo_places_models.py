from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    DROP TABLE `places_extra`;
""",
"""
    CREATE TABLE `places_extra` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `created_at` datetime NOT NULL,
        `created_by_id` integer NOT NULL,
        `modified_at` datetime NOT NULL,
        `modified_by_id` integer NOT NULL,
        `place_id` integer NOT NULL,
        `text_desc` varchar(200) NULL,
        `file` varchar(100) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `places_extra` ADD CONSTRAINT created_by_id_refs_id_281857ff FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
""", """
    ALTER TABLE `places_extra` ADD CONSTRAINT modified_by_id_refs_id_281857ff FOREIGN KEY (`modified_by_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `places_extra`;
"""])
