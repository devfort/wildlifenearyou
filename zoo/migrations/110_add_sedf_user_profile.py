from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    DELETE FROM `accounts_profile`
""","""    
    INSERT INTO `accounts_profile` VALUES (1,1,1,'','',100,0)
"""], sql_down=["""
"""])

