from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `changerequests_createobjectrequest` (
        `changerequest_ptr_id` integer NOT NULL PRIMARY KEY,
        `parent_id` integer NOT NULL,
        `content_type_id` integer NOT NULL,
        `attributes` longtext NOT NULL,
        `reverse_relation` longtext NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `changerequests_createobjectrequest` ADD CONSTRAINT content_type_id_refs_id_4405da2f FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);
"""], sql_down=["""
    DROP TABLE `changerequests_createobjectrequest`;
"""])
