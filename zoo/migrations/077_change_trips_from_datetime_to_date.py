from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime

migration = m.Migration(sql_up=[
    """ALTER TABLE `trips_trip` MODIFY `id` date""",
    """ ALTER TABLE `trips_trip` MODIFY `id` date"""
], sql_down=[
    """ALTER TABLE `trips_trip` MODIFY `id` datetime NOT NULL""",
    """ALTER TABLE `trips_trip` MODIFY `id` datetime NOT NULL"""
])
