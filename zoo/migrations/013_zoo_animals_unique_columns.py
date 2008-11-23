from dmigrations.mysql import migrations as m

class CustomMigration(m.Migration):
    def __init__(self):
        sql_up = ["""
alter table animals_animal change column slug slug varchar(255);
alter table animals_animalclass change column name name varchar(255);
create unique index animals_animal_slug_idx on animals_animal(slug);
create unique index animals_animalclass_name_idx on animals_animalclass(name);
"""]
        sql_down = ["""
drop index animals_animal_slug_idx on animals_animal; alter table animals_animal change column slug slug varchar(500);
drop index animals_animalclass_name_idx on animals_animalclass; alter table animals_animalclass change column name name varchar(500);
"""]
        super(CustomMigration, self).__init__(
            sql_up=sql_up, sql_down=sql_down
        )

migration = CustomMigration()
