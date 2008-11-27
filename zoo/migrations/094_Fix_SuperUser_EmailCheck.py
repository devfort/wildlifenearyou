from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    UPDATE accounts_profile SET `email_validated` = 1 WHERE user_id = 1
"""], sql_down=["""
    UPDATE accounts_profile SET `email_validated` = 0 WHERE user_id = 1
"""])