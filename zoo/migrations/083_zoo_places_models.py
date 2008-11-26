from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    ALTER TABLE `places_placedirection` DROP COLUMN `mode`;
""","""
    ALTER TABLE `places_placedirection` ADD COLUMN `mode_id` INTEGER NOT NULL;
""","""
    CREATE TABLE `places_transporttypes` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `icon` varchar(100) NOT NULL,
        `default_desc` varchar(200) NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    INSERT INTO `places_currency` VALUES (3,'Yen','YEN')    
""", """
    INSERT INTO `places_transporttypes` VALUES (1,'','Car')
""", """
    INSERT INTO `places_transporttypes` VALUES (2,'','Bus')
""", """
    INSERT INTO `places_transporttypes` VALUES (3,'','Train')
""", """
    INSERT INTO `places_transporttypes` VALUES (4,'','Bike')
""", """
    INSERT INTO `places_transporttypes` VALUES (5,'','Foot')
""", """
    INSERT INTO `places_transporttypes` VALUES (6,'','Plane')
""", """
    INSERT INTO `places_transporttypes` VALUES (7,'','Helicopter')
""", """
    INSERT INTO `places_transporttypes` VALUES (8,'','Zeppelin')
""", """
    INSERT INTO `places_transporttypes` VALUES (9,'','Boat')
""", """
    INSERT INTO `places_transporttypes` VALUES (10,'','Ferry')
""", """
    INSERT INTO `places_transporttypes` VALUES (11,'','UFO')
""", """
    INSERT INTO `places_transporttypes` VALUES (12,'','Narwhal')
""", """
    INSERT INTO `places_transporttypes` VALUES (13,'','Teleporter')
"""], sql_down=["""
    DROP TABLE `places_transporttypes`;
""", """
    DROP TABLE `places_placedirection`;
"""])