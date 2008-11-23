from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `places_webcam` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `place_id` integer NOT NULL,
        `name` varchar(300) NULL,
        `url` varchar(200) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
"""], sql_down=["""
    DROP TABLE `places_webcam`;
"""])
