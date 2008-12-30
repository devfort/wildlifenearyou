from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime

class CustomMigration(m.Migration):
    def __init__(self):
        pass
    
    def up(self):
        # First we convert existing inexact sightings in to regulars
        existing = self.execute_sql(
            """
            SELECT 
                created_at,
                created_by_id,
                species,
                place_id,
                trip_id,
                modified_at,
                modified_by_id
            FROM trips_inexactsighting
            """, return_rows=True
        )
        self.execute_sql(["""
            DROP TABLE `trips_inexactsighting`;
        """])
        # Now insert them all again
        for row in existing:
            self.execute_sql(["""
                INSERT INTO `trips_sighting` 
                    (created_at, created_by_id, species_inexact, 
                    place_id, trip_id, modified_at, modified_by_id)
                VALUES
                    ('%s', '%s', '%s', '%s', '%s', '%s', '%s')
            """ % row])
    
    def down(self):
        self.execute_sql([
        """
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
        """]
        )
migration = CustomMigration()
