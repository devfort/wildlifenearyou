from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
m1 = m.Migration(sql_up=["""
    CREATE TABLE `changerequests_changerequest` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `applied_at` datetime NULL,
        `applied_by_id` integer NULL,
        `subclass` varchar(100) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `changerequests_changerequest` ADD CONSTRAINT applied_by_id_refs_id_2a09739c FOREIGN KEY (`applied_by_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `changerequests_changerequest`;
"""])
m2 = m.AddColumn('changerequests', 'changerequest', 'group', 'integer NOT NULL', 'changerequests_changerequestgroup')

migration = m.Compound([m1, m2])
