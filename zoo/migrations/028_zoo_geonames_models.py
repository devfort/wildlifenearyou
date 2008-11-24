from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `geonames_geoname` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `country_code` varchar(2) NOT NULL,
        `postal_code` varchar(10) NOT NULL,
        `place_name` varchar(180) NOT NULL,
        `admin_name1` varchar(100) NOT NULL,
        `admin_code1` varchar(20) NOT NULL,
        `admin_name2` varchar(100) NOT NULL,
        `admin_code2` varchar(20) NOT NULL,
        `admin_name3` varchar(100) NOT NULL,
        `latitude` varchar(20) NOT NULL,
        `longitude` varchar(20) NOT NULL,
        `accuracy` varchar(10) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
"""], sql_down=["""
    DROP TABLE `geonames_geoname`;
"""])
