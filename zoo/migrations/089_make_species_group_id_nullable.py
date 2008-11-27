from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    ALTER TABLE `animals_species` CHANGE COLUMN `species_group_id`
    `species_group_id` int(11) null
"""], sql_down=["""
    ALTER TABLE `animals_species` CHANGE COLUMN `species_group_id`
    `species_group_id` int(11) not null
"""])
