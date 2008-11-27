from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m

migration = m.Compound([
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
        'animals', 'species', 'created_by', 'integer NOT NULL', 'auth_user'
    ),
    m.DropColumn(
        'animals', 'species', 'modified_by', 'integer NOT NULL', 'auth_user'
    ),
    m.DropColumn(
        'animals', 'superspecies', 'created_by', 'integer NOT NULL', 'auth_user'
    ),
    m.DropColumn(
        'animals', 'superspecies', 'modified_by', 'integer NOT NULL', 'auth_user'
    ),
])

