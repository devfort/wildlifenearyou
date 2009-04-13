from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `blog_categories` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `title` varchar(100) NOT NULL,
        `slug` varchar(50) NOT NULL UNIQUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `blog_posts` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `title` varchar(200) NOT NULL,
        `slug` varchar(50) NOT NULL,
        `author_id` integer NULL,
        `body` longtext NOT NULL,
        `tease` longtext NOT NULL,
        `status` integer NOT NULL,
        `allow_comments` bool NOT NULL,
        `publish` datetime NOT NULL,
        `created` datetime NOT NULL,
        `modified` datetime NOT NULL,
        `tags` varchar(255) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `blog_posts` ADD CONSTRAINT author_id_refs_id_1086af0a FOREIGN KEY (`author_id`) REFERENCES `auth_user` (`id`);
""", """
    CREATE TABLE `blog_posts_categories` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `post_id` integer NOT NULL,
        `category_id` integer NOT NULL,
        UNIQUE (`post_id`, `category_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `blog_posts_categories` ADD CONSTRAINT post_id_refs_id_290ed72f FOREIGN KEY (`post_id`) REFERENCES `blog_posts` (`id`);
""", """
    ALTER TABLE `blog_posts_categories` ADD CONSTRAINT category_id_refs_id_6ef31e9d FOREIGN KEY (`category_id`) REFERENCES `blog_categories` (`id`);
"""], sql_down=["""
    DROP TABLE `blog_posts_categories`;
""", """
    DROP TABLE `blog_posts`;
""", """
    DROP TABLE `blog_categories`;
"""])
