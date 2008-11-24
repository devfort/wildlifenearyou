from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Compound([
    
    # First drop the current photos table (don't try and save old data)
    m.Migration(sql_up=["""
        DROP TABLE `photos_photo`;
    """], sql_down=["""
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
    """]),
    
    # Now create the new one
    m.Migration(sql_up=["""
        CREATE TABLE `photos_photo` (
            `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
            `created_by_id` integer NOT NULL,
            `created_at` datetime NOT NULL,
            `title` varchar(255) NOT NULL,
            `photo` varchar(100) NOT NULL,
            `trip_id` integer NULL,
            `place_id` integer NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8
        ;
    """, """
        ALTER TABLE `photos_photo` ADD CONSTRAINT created_by_id_refs_id_5d63593a FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
    """, """
        ALTER TABLE `photos_photo` ADD CONSTRAINT trip_id_refs_id_16d32727 FOREIGN KEY (`trip_id`) REFERENCES `trips_trip` (`id`);
    """, """
        ALTER TABLE `photos_photo` ADD CONSTRAINT place_id_refs_id_3a7395a5 FOREIGN KEY (`place_id`) REFERENCES `places_place` (`id`);
    """, """
        CREATE TABLE `photos_photo_contained_species` (
            `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
            `photo_id` integer NOT NULL,
            `species_id` integer NOT NULL,
            UNIQUE (`photo_id`, `species_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8
        ;
    """, """
        ALTER TABLE `photos_photo_contained_species` ADD CONSTRAINT photo_id_refs_id_38fa3104 FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`);
    """, """
        ALTER TABLE `photos_photo_contained_species` ADD CONSTRAINT species_id_refs_id_13bab37 FOREIGN KEY (`species_id`) REFERENCES `animals_species` (`id`);
    """], sql_down=["""
        DROP TABLE `photos_photo_contained_species`;
    """, """
        DROP TABLE `photos_photo`;
    """])
])
