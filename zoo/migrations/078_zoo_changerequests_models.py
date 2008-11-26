from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `changerequests_deleteobjectrequest` (
        `changerequest_ptr_id` integer NOT NULL PRIMARY KEY,
        `content_type_id` integer NOT NULL,
        `object_id` integer UNSIGNED NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `changerequests_deleteobjectrequest` ADD CONSTRAINT content_type_id_refs_id_6e0b4962 FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);
"""], sql_down=["""
    DROP TABLE `changerequests_deleteobjectrequest`;
"""])
