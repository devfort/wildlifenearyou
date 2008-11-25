from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `trips_sighting` (
        `id` integer NOT NULL PRIMARY KEY,
        `created_at` datetime NOT NULL,
        `created_by_id` integer NOT NULL REFERENCES `auth_user` (`id`),
        `modified_at` datetime NOT NULL,
        `modified_by_id` integer NOT NULL REFERENCES `auth_user` (`id`),
        `place_id` integer NOT NULL REFERENCES `places_place` (`id`),
        `species_id` integer NOT NULL REFERENCES `animals_species` (`id`),
        `trip_id` integer NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    DROP TABLE `trips_tripsighting`;
""", """
    UPDATE `trips_trip` SET
        created_by_id  = user_id, created_at  = current_timestamp,
        modified_by_id = user_id, modified_at = current_timestamp
""", """
    ALTER TABLE `trips_trip` DROP FOREIGN KEY user_id_refs_id_2b6daa0c;
""", """
    ALTER TABLE `trips_trip` DROP COLUMN `user_id`;
"""
], sql_down=["""
    DROP TABLE `trips_sighting`;
""", """
    CREATE TABLE `trips_tripsighting` (
        `id` integer NOT NULL PRIMARY KEY,
        `created_at` datetime NOT NULL,
        `created_by_id` integer NOT NULL REFERENCES `auth_user` (`id`),
        `modified_at` datetime NOT NULL,
        `modified_by_id` integer NOT NULL REFERENCES `auth_user` (`id`),
        `species_id` integer NOT NULL REFERENCES `animals_species` (`id`),
        `trip_id` integer NOT NULL REFERENCES `trips_trip` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `trips_trip` ADD `user_id` integer NOT NULL REFERENCES `auth_user` (`id`)
""", """
    ALTER TABLE `trips_trip` ADD CONSTRAINT user_id_refs_id_2b6daa0c FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
"""
])
