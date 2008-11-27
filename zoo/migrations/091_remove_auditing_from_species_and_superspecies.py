from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m

migration = m.Compound([
    m.Migration(
        sql_up = ['''
            ALTER TABLE animals_superspecies 
            DROP FOREIGN KEY created_by_id_refs_id_5a9fbc3b;
        ''', '''
            ALTER TABLE animals_superspecies 
            DROP FOREIGN KEY modified_by_id_refs_id_5a9fbc3b;
        '''], sql_down = [""]
    ),
    m.DropColumn(
        'animals', 'species', 'created_at', 'datetime NOT NULL'
    ),
    m.DropColumn(
        'animals', 'species', 'modified_at', 'datetime NOT NULL'
    ),
    m.DropColumn(
        'animals', 'superspecies', 'created_at', 'datetime NOT NULL'
    ),
    m.DropColumn(
        'animals', 'superspecies', 'modified_at', 'datetime NOT NULL'
    ),
    m.DropColumn(
        'animals', 'species', 'created_by', 'integer NOT NULL',
    ),
    m.DropColumn(
        'animals', 'species', 'modified_by', 'integer NOT NULL',
    ),
    m.DropColumn(
        'animals', 'superspecies', 'created_by', 'integer NOT NULL',
    ),
    m.DropColumn(
        'animals', 'superspecies', 'modified_by', 'integer NOT NULL',
    ),
])

