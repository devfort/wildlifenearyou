from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `favourites_favouritespecies` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `user_id` integer NOT NULL,
        `species_id` integer NOT NULL,
        `when_added` datetime NOT NULL,
        UNIQUE (`user_id`, `species_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `favourites_favouritespecies` ADD CONSTRAINT species_id_refs_id_4255f8bb FOREIGN KEY (`species_id`) REFERENCES `animals_species` (`id`);
""", """
    ALTER TABLE `favourites_favouritespecies` ADD CONSTRAINT user_id_refs_id_56baecc7 FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `favourites_favouritespecies`;
"""])
