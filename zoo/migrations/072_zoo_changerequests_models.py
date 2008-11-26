from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `changerequests_changeattributerequest` (
        `changerequest_ptr_id` integer NOT NULL PRIMARY KEY,
        `content_type_id` integer NOT NULL,
        `object_id` integer UNSIGNED NOT NULL,
        `attribute` varchar(100) NOT NULL,
        `old_value` longtext NOT NULL,
        `new_value` longtext NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `changerequests_changeattributerequest` ADD CONSTRAINT content_type_id_refs_id_4857dd9 FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);
"""], sql_down=["""
    DROP TABLE `changerequests_changeattributerequest`;
"""])
