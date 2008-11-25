from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `django_flatpage` (
        `id` integer NOT NULL PRIMARY KEY,
        `url` varchar(100) NOT NULL,
        `title` varchar(200) NOT NULL,
        `content` text NOT NULL,
        `enable_comments` bool NOT NULL,
        `template_name` varchar(70) NOT NULL,
        `registration_required` bool NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `django_flatpage_sites` (
        `id` integer NOT NULL PRIMARY KEY,
        `flatpage_id` integer NOT NULL REFERENCES `django_flatpage` (`id`),
        `site_id` integer NOT NULL REFERENCES `django_site` (`id`),
        UNIQUE (`flatpage_id`, `site_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
"""], sql_down=["""
    DROP TABLE `django_flatpage_sites`;
""", """
    DROP TABLE `django_flatpage`;
"""])
