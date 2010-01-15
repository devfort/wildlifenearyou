from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    DROP TABLE `rspb_rspbbirdpage`;
""",
"""
    CREATE TABLE `rspb_rspbbirdpage` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(255) NOT NULL,
        `url` varchar(255) NOT NULL,
        `image_url` varchar(255) NOT NULL,
        `teaser` longtext NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `rspb_rspbbirdpage_species` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `rspbbirdpage_id` integer NOT NULL,
        `species_id` integer NOT NULL,
        UNIQUE (`rspbbirdpage_id`, `species_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `rspb_rspbbirdpage_species` ADD CONSTRAINT `rspbbirdpage_id_refs_id_58b6a9bc` FOREIGN KEY (`rspbbirdpage_id`) REFERENCES `rspb_rspbbirdpage` (`id`);
""", """
    ALTER TABLE `rspb_rspbbirdpage_species` ADD CONSTRAINT `species_id_refs_id_6083130f` FOREIGN KEY (`species_id`) REFERENCES `animals_species` (`id`);
"""], sql_down=["""
    DROP TABLE `rspb_rspbbirdpage_species`;
""", """
    DROP TABLE `rspb_rspbbirdpage`;
""", """
    CREATE TABLE `rspb_rspbbirdpage` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `name` varchar(255) NOT NULL,
        `species_id` integer,
        `url` varchar(255) NOT NULL,
        `image_url` varchar(255) NOT NULL,
        `teaser` longtext NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ;
    """, """
        ALTER TABLE `rspb_rspbbirdpage` ADD CONSTRAINT `species_id_refs_id_a230c37a` FOREIGN KEY (`species_id`) REFERENCES `animals_species` (`id`);
    """]
)
