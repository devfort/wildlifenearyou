from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    UPDATE `places_country` SET `country_code` = LOWER(`country_code`);
"""], sql_down=["""
    UPDATE `places_country` SET `country_code` = UPPER(`country_code`);
"""])