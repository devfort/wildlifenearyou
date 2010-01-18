from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `cleanup_placeneedscleanup` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `place_id` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `cleanup_placeneedscleanup` ADD CONSTRAINT `place_id_refs_id_8d1ba87d` FOREIGN KEY (`place_id`) REFERENCES `places_place` (`id`);
"""], sql_down=["""
    DROP TABLE `cleanup_placeneedscleanup`;
"""])
