from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE "places_placeopening" (
        "id" integer NOT NULL PRIMARY KEY,
        "start_date" date NULL,
        "end_date" date NULL,
        "days_of_week" varchar(100) NOT NULL,
        "times" varchar(100) NOT NULL,
        "closed" bool NOT NULL,
        "place_id" integer NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
"""], sql_down=["""
    DROP TABLE "places_placeopening";
"""])
