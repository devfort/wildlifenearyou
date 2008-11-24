from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `trips_trip` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `start` datetime NOT NULL,
        `end` datetime NOT NULL,
        `place_id` integer NOT NULL,
        `user_id` integer NOT NULL,
        `name` varchar(100) NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `trips_trip` ADD CONSTRAINT place_id_refs_id_2ede8a1 FOREIGN KEY (`place_id`) REFERENCES `places_place` (`id`);
""", """
    ALTER TABLE `trips_trip` ADD CONSTRAINT user_id_refs_id_2b6daa0c FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `trips_trip`;
"""])
