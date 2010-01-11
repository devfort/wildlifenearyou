from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `flickr_flickrset` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `flickr_id` varchar(100) NOT NULL,
        `title` varchar(255) NOT NULL,
        `description` longtext NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `flickr_flickrset_photos` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `flickrset_id` integer NOT NULL,
        `photo_id` integer NOT NULL,
        UNIQUE (`flickrset_id`, `photo_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `flickr_flickrset_photos` ADD CONSTRAINT `flickrset_id_refs_id_59c7d150` FOREIGN KEY (`flickrset_id`) REFERENCES `flickr_flickrset` (`id`);
""", """
    ALTER TABLE `flickr_flickrset_photos` ADD CONSTRAINT `photo_id_refs_id_639f7e5` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`);
"""], sql_down=["""
    DROP TABLE `flickr_flickrset_photos`;
""", """
    DROP TABLE `flickr_flickrset`;
"""])
