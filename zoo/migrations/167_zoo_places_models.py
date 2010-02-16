from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `places_placeredirect` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `slug` varchar(255) NOT NULL UNIQUE,
        `country_id` integer NOT NULL,
        `redirect_to` varchar(255) NOT NULL,
        `created` datetime NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
"""], sql_down=["""
    DROP TABLE `places_placeredirect`;
"""])
