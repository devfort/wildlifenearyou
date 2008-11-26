from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `places_facility` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `icon` varchar(100) NOT NULL,
        `default_desc` varchar(200) NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
"""], sql_down=["""
    DROP TABLE `places_facility`;
"""])
