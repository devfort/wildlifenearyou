from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `feedback_feedback` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `user_id` integer NULL,
        `email` varchar(75) NOT NULL,
        `ip_address` varchar(40) NOT NULL,
        `from_page` varchar(255) NOT NULL,
        `created` datetime NOT NULL,
        `body` longtext NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `feedback_feedback` ADD CONSTRAINT user_id_refs_id_7d59e8d4 FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `feedback_feedback`;
"""])
