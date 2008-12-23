from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `django_openid_nonce` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `server_url` varchar(255) NOT NULL,
        `timestamp` integer NOT NULL,
        `salt` varchar(40) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `django_openid_association` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `server_url` longtext NOT NULL,
        `handle` varchar(255) NOT NULL,
        `secret` longtext NOT NULL,
        `issued` integer NOT NULL,
        `lifetime` integer NOT NULL,
        `assoc_type` longtext NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `django_openid_useropenidassociation` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `user_id` integer NOT NULL,
        `openid` varchar(255) NOT NULL,
        `created` datetime NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `django_openid_useropenidassociation` ADD CONSTRAINT user_id_refs_id_7b6741ee FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `django_openid_useropenidassociation`;
""", """
    DROP TABLE `django_openid_association`;
""", """
    DROP TABLE `django_openid_nonce`;
"""])
