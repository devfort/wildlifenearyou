from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `changerequests_changerequestgroup` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `created_at` datetime NOT NULL,
        `created_by_id` integer NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `changerequests_changerequestgroup` ADD CONSTRAINT created_by_id_refs_id_72efcba0 FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `changerequests_changerequestgroup`;
"""])
