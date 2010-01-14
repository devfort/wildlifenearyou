from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `photos_suggestedspecies` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `photo_id` integer NOT NULL,
        `species_id` integer,
        `species_inexact` varchar(100) NOT NULL,
        `suggested_by_id` integer NOT NULL,
        `suggested_at` datetime NOT NULL,
        `denorm_suggestion_for_id` integer NOT NULL,
        `note` longtext NOT NULL,
        `status` varchar(20) NOT NULL,
        `status_changed_at` datetime
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `photos_suggestedspecies` ADD CONSTRAINT `species_id_refs_id_288414d6` FOREIGN KEY (`species_id`) REFERENCES `animals_species` (`id`);
""", """
    ALTER TABLE `photos_suggestedspecies` ADD CONSTRAINT `suggested_by_id_refs_id_1ce5d06c` FOREIGN KEY (`suggested_by_id`) REFERENCES `auth_user` (`id`);
""", """
    ALTER TABLE `photos_suggestedspecies` ADD CONSTRAINT `denorm_suggestion_for_id_refs_id_1ce5d06c` FOREIGN KEY (`denorm_suggestion_for_id`) REFERENCES `auth_user` (`id`);
""", """
    ALTER TABLE `photos_suggestedspecies` ADD CONSTRAINT `photo_id_refs_id_f3ac901d` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`);
"""], sql_down=["""
    DROP TABLE `photos_suggestedspecies`;
"""])
