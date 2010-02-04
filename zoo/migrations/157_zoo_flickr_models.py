from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `flickr_flickrtagsapplied` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `photo_id` integer NOT NULL,
        `tags_added` longtext NOT NULL,
        `latitude_added` double precision,
        `longitude_added` double precision,
        `created_at` datetime NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `flickr_flickrtagsapplied` ADD CONSTRAINT `photo_id_refs_id_7fa8b78c` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`);
"""], sql_down=["""
    DROP TABLE `flickr_flickrtagsapplied`;
"""])
