from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `trips_inexactsighting` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `created_at` datetime NOT NULL,
        `created_by_id` integer NOT NULL,
        `modified_at` datetime NOT NULL,
        `modified_by_id` integer NOT NULL,
        `species` varchar(100) NOT NULL,
        `place_id` integer NOT NULL,
        `trip_id` integer NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `trips_inexactsighting` ADD CONSTRAINT created_by_id_refs_id_18e810ff FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
""", """
    ALTER TABLE `trips_inexactsighting` ADD CONSTRAINT modified_by_id_refs_id_18e810ff FOREIGN KEY (`modified_by_id`) REFERENCES `auth_user` (`id`);
""", """
    ALTER TABLE `trips_inexactsighting` ADD CONSTRAINT place_id_refs_id_5b85ed4 FOREIGN KEY (`place_id`) REFERENCES `places_place` (`id`);
"""], sql_down=["""
    DROP TABLE `trips_inexactsighting`;
"""])
