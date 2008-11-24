from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `django_comments` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `content_type_id` integer NOT NULL,
        `object_pk` longtext NOT NULL,
        `site_id` integer NOT NULL,
        `user_id` integer NULL,
        `user_name` varchar(50) NOT NULL,
        `user_email` varchar(75) NOT NULL,
        `user_url` varchar(200) NOT NULL,
        `comment` longtext NOT NULL,
        `submit_date` datetime NOT NULL,
        `ip_address` char(15) NULL,
        `is_public` bool NOT NULL,
        `is_removed` bool NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `django_comments` ADD CONSTRAINT content_type_id_refs_id_d5868a5 FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);
""", """
    ALTER TABLE `django_comments` ADD CONSTRAINT site_id_refs_id_7248df08 FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`);
""", """
    ALTER TABLE `django_comments` ADD CONSTRAINT user_id_refs_id_7e9ddfef FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
""", """
    CREATE TABLE `django_comment_flags` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `user_id` integer NOT NULL,
        `comment_id` integer NOT NULL,
        `flag` varchar(30) NOT NULL,
        `flag_date` datetime NOT NULL,
        UNIQUE (`user_id`, `comment_id`, `flag`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `django_comment_flags` ADD CONSTRAINT user_id_refs_id_603c4dcb FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
""", """
    ALTER TABLE `django_comment_flags` ADD CONSTRAINT comment_id_refs_id_373a05f7 FOREIGN KEY (`comment_id`) REFERENCES `django_comments` (`id`);
"""], sql_down=["""
    DROP TABLE `django_comment_flags`;
""", """
    DROP TABLE `django_comments`;
"""])
