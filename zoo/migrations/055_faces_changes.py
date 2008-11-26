from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime

migration = m.Compound([
    m.Migration(sql_up=["""
        CREATE TABLE `faces_faceareacategory` (
            `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
            `name` varchar(100) NOT NULL,
            `is_special` bool NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8
        ;
    """], sql_down=["""
        DROP TABLE `faces_faceareacategory`;
    """]),
    m.AddColumn('faces', 'facearea', 'category', 'integer NULL', 'faces_faceareacategory'),
    m.AddColumn('faces', 'facearea', 'order', 'integer NULL'),
    m.Migration(sql_up=["""
        CREATE TABLE `faces_specialpermission` (
            `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
            `category_id` integer NOT NULL,
            `user_id` integer NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8
        ;
    """, """
        ALTER TABLE `faces_specialpermission` ADD CONSTRAINT user_id_refs_id_44e8cf58 FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
    """], sql_down=["""
        DROP TABLE `faces_specialpermission`;
    """])
])
