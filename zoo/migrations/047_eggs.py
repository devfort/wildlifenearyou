from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m

class CustomMigration(m.Migration):
    def __init__(self):
        sql_up = ["""
INSERT INTO `animals_superspecies` VALUES (1,'2008-11-25 05:12:29',1,'2008-11-25 05:12:29',1,'Dodo','dodo','extinct','raphus-cucullatus',NULL)
""","""
insert into `animals_superspecies` VALUES (2,'2008-11-25 05:13:29',1,'2008-11-25 05:14:20',1,'Woolly Mammoth','woolly-mammoth','extinct','',NULL)
""","""
INSERT INTO `animals_superspecies` VALUES (3,'2008-11-25 05:15:11',1,'2008-11-25 05:15:11',1,'Unicorn','unicorn','imaginary','',NULL)
""","""
INSERT INTO `animals_superspecies` VALUES (4,'2008-11-25 05:16:00',1,'2008-11-25 05:16:00',1,'Werewolf','werewolf','imaginary','',NULL)
""","""
INSERT INTO `animals_superspecies` VALUES (5,'2008-11-25 05:16:38',1,'2008-11-25 05:16:38',1,'Dragon','dragon','imaginary','',NULL)
""","""
INSERT INTO `animals_superspecies` VALUES (6,'2008-11-25 05:16:47',1,'2008-11-25 05:16:47',1,'Chimera','chimera','imaginary','',NULL)
""","""
INSERT INTO `animals_superspecies` VALUES (7,'2008-11-25 05:17:07',1,'2008-11-25 05:17:07',1,'Gryphon','gryphon','imaginary','',NULL)
""","""
INSERT INTO `animals_superspecies` VALUES (8,'2008-11-25 05:17:22',1,'2008-11-25 05:17:22',1,'Narwhal','narwhals','narwhals','',NULL)
"""]
        sql_down = [
"DELETE FROM `animals_superspecies`"
]
        super(CustomMigration, self).__init__(
            sql_up=sql_up, sql_down=sql_down
        )
    # Or override the up() and down() methods

migration = CustomMigration()
