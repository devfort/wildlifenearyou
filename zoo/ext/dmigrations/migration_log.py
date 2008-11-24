import datetime
from migration_state import _execute, _execute_in_transaction, table_present
from django.conf import settings
from django.db import connection

if settings.DATABASE_ENGINE == 'mysql':
    MIGRATION_LOG_SQL = """
    CREATE TABLE `dmigrations_log` (
    `id` int(11) NOT NULL auto_increment,
    `action` VARCHAR(255) NOT NULL,
    `migration` VARCHAR(255) NOT NULL,
    `status` VARCHAR(255) NOT NULL,
    `datetime` DATETIME NOT NULL,
     PRIMARY KEY  (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8
"""
elif settings.DATABASE_ENGINE == 'sqlite3':
    MIGRATION_LOG_SQL = """
    CREATE TABLE `dmigrations_log` (
    `id` integer NOT NULL primary key,
    `action` VARCHAR(255) NOT NULL,
    `migration` VARCHAR(255) NOT NULL,
    `status` VARCHAR(255) NOT NULL,
    `datetime` DATETIME NOT NULL
    )
"""

def init():
    """
    Create migration log if it doesn't exist
    """
    if not table_present('dmigrations_log'):
      _execute(MIGRATION_LOG_SQL)

def get_log():
    return list(_execute("""
        SELECT action, migration, status, datetime
        FROM dmigrations_log
        ORDER BY datetime, id"""
    ).fetchall())

def log_action(action, migration, status, when=None):
    if when == None:
        when = datetime.datetime.now()
    statement = """
        INSERT INTO dmigrations_log(action, migration, status, datetime)
        VALUES (%s, %s, %s, %s)
    """
    params = [action, migration, status, when]
    # Should work fine in transaction for SQLite3, but gives
    # logic error or database not found error?!
    if settings.DATABASE_ENGINE == 'mysql':
        _execute_in_transaction(statement, params)
    elif settings.DATABASE_ENGINE == 'sqlite3':
        _execute(statement, params)
        cursor = connection.cursor()
        cursor.cursor.connection.commit()

