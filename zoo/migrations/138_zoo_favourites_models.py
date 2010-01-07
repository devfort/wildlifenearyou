from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `favourites_favouritephoto` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `user_id` integer NOT NULL,
        `photo_id` integer NOT NULL,
        `when_added` datetime NOT NULL,
        UNIQUE (`user_id`, `photo_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `favourites_favouritephoto` ADD CONSTRAINT `user_id_refs_id_782f1c1d` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
""", """
    ALTER TABLE `favourites_favouritephoto` ADD CONSTRAINT `photo_id_refs_id_10142c6c` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`);
"""], sql_down=["""
    DROP TABLE `favourites_favouritephoto`;
"""])
