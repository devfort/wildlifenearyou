from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `schedule_rule` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(32) NOT NULL,
        `description` longtext NOT NULL,
        `frequency` varchar(10) NOT NULL,
        `params` longtext NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `schedule_event` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `start` datetime NOT NULL,
        `end` datetime NOT NULL,
        `title` varchar(255) NOT NULL,
        `description` longtext NULL,
        `creator_id` integer NULL,
        `created_on` datetime NOT NULL,
        `end_recurring_period` datetime NULL,
        `rule_id` integer NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `schedule_event` ADD CONSTRAINT creator_id_refs_id_6d7cb7f0 FOREIGN KEY (`creator_id`) REFERENCES `auth_user` (`id`);
""", """
    ALTER TABLE `schedule_event` ADD CONSTRAINT rule_id_refs_id_747df0fc FOREIGN KEY (`rule_id`) REFERENCES `schedule_rule` (`id`);
""", """
    CREATE TABLE `schedule_calendar` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(200) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `schedule_calendarrelation` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `calendar_id` integer NOT NULL,
        `content_type_id` integer NOT NULL,
        `object_id` integer NOT NULL,
        `distinction` varchar(20) NULL,
        `inheritable` bool NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `schedule_calendarrelation` ADD CONSTRAINT calendar_id_refs_id_679e6b27 FOREIGN KEY (`calendar_id`) REFERENCES `schedule_calendar` (`id`);
""", """
    ALTER TABLE `schedule_calendarrelation` ADD CONSTRAINT content_type_id_refs_id_1789be3d FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);
""", """
    CREATE TABLE `schedule_eventrelation` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `event_id` integer NOT NULL,
        `content_type_id` integer NOT NULL,
        `object_id` integer NOT NULL,
        `distinction` varchar(20) NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `schedule_eventrelation` ADD CONSTRAINT event_id_refs_id_6921d83b FOREIGN KEY (`event_id`) REFERENCES `schedule_event` (`id`);
""", """
    ALTER TABLE `schedule_eventrelation` ADD CONSTRAINT content_type_id_refs_id_1db76564 FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);
""", """
    CREATE TABLE `schedule_calendar_events` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `calendar_id` integer NOT NULL,
        `event_id` integer NOT NULL,
        UNIQUE (`calendar_id`, `event_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `schedule_calendar_events` ADD CONSTRAINT calendar_id_refs_id_164a4e1c FOREIGN KEY (`calendar_id`) REFERENCES `schedule_calendar` (`id`);
""", """
    ALTER TABLE `schedule_calendar_events` ADD CONSTRAINT event_id_refs_id_19eeaa7 FOREIGN KEY (`event_id`) REFERENCES `schedule_event` (`id`);
"""], sql_down=["""
    DROP TABLE `schedule_calendar_events`;
""", """
    DROP TABLE `schedule_eventrelation`;
""", """
    DROP TABLE `schedule_calendarrelation`;
""", """
    DROP TABLE `schedule_calendar`;
""", """
    DROP TABLE `schedule_event`;
""", """
    DROP TABLE `schedule_rule`;
"""])
