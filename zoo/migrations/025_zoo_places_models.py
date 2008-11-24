from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `places_placenews` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `place_id` integer NOT NULL,
        `headline` varchar(300) NOT NULL,
        `url` varchar(200) NOT NULL,
        `story_date` date NOT NULL,
        `created_at` datetime NOT NULL,
        `created_by_id` integer NOT NULL,
        `modified_at` datetime NOT NULL,
        `modified_by_id` integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `places_placenews` ADD CONSTRAINT created_by_id_refs_id_1ed4276b FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
""", """
    ALTER TABLE `places_placenews` ADD CONSTRAINT modified_by_id_refs_id_1ed4276b FOREIGN KEY (`modified_by_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `places_placenews`;
"""])
