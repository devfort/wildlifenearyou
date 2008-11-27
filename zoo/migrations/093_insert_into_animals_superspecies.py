from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime
migration = m.InsertRows(
    table_name = 'animals_superspecies',
    columns = [u'id', u'common_name', u'slug', u'type', u'latin_name', u'species_group_id', u'description'],
    insert_rows = ((1L,
  u'Dodo',
  u'dodo',
  u'extinct',
  u'raphus cucullatus',
  None,
  u''),
 (2L,
  u'Woolly Mammoth',
  u'woolly-mammoth',
  u'extinct',
  u'mammuthus primigenius',
  None,
  u''),
 (3L,
  u'Unicorn',
  u'unicorn',
  u'imaginary',
  u'equus unicornis',
  None,
  u''),
 (4L,
  u'Werewolf',
  u'werewolf',
  u'imaginary',
  u'homo lycanthropus',
  None,
  u''),
 (5L,
  u'Dragon',
  u'dragon',
  u'imaginary',
  u'draco draco',
  None,
  u''),
 (6L,
  u'Chimera',
  u'chimera',
  u'imaginary',
  u'chimaera chimaera',
  None,
  u''),
 (7L,
  u'Gryphon',
  u'gryphon',
  u'imaginary',
  u'gryphus',
  None,
  u''),
 (8L,
  u'Narwhal',
  u'narwhals',
  u'narwhals',
  u'monodon monocerosusess',
  None,
  u'')),
    delete_ids = [1, 2, 3, 4, 5, 6, 7, 8]
)
