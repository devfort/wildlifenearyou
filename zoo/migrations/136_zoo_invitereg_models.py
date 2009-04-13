from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `invitereg_invitecode` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `code` varchar(20) NOT NULL,
        `claimed` bool NOT NULL,
        `claimed_at` datetime NULL,
        `claimed_by_id` integer NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `invitereg_invitecode` ADD CONSTRAINT claimed_by_id_refs_id_2ce6c6ba FOREIGN KEY (`claimed_by_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `invitereg_invitecode`;
"""])
