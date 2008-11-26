from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime

migration = m.Migration(sql_up=["""
    ALTER TABLE `places_placeopening` MODIFY `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY
""","""
    ALTER TABLE `django_flatpage` MODIFY `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY
""","""
    ALTER TABLE `django_flatpage_sites` MODIFY `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY
""","""
    ALTER TABLE `trips_sighting` MODIFY `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY
"""
], sql_down=[])
