from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `places_placeprice` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `created_at` datetime NOT NULL,
        `created_by_id` integer NOT NULL,
        `modified_at` datetime NOT NULL,
        `modified_by_id` integer NOT NULL,
        `place_id` integer NOT NULL,
        `currency_id` integer NOT NULL,
        `type` varchar(100) NOT NULL,
        `value` numeric(12, 2) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `places_placeprice` ADD CONSTRAINT created_by_id_refs_id_37ed4278 FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
""", """
    ALTER TABLE `places_placeprice` ADD CONSTRAINT modified_by_id_refs_id_37ed4278 FOREIGN KEY (`modified_by_id`) REFERENCES `auth_user` (`id`);
""", """
    CREATE TABLE `places_currency` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(100) NOT NULL,
        `currency_code` varchar(3) NOT NULL UNIQUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    INSERT INTO `places_currency` VALUES (1,'British Sterling', 'GBP')
""", """
    INSERT INTO `places_currency` VALUES (2,'United States Dollar', 'USD')
"""], sql_down=["""
    DROP TABLE `places_placeprice`;
""","""
    DROP TABLE `places_currency`;
"""])
