from dmigrations.mysql import migrations as m
import datetime
migration = m.InsertRows(
    table_name = 'auth_user',
    columns = [u'id', u'username', u'first_name', u'last_name', u'email', u'password', u'is_staff', u'is_active', u'is_superuser', u'last_login', u'date_joined'],
    insert_rows = ((1L,
  u'sedf',
  u'',
  u'',
  u'sedf@example.com',
  u'sha1$ee75e$5f8e94a81d9a05879445d99c4770b823cf12cd07',
  1,
  1,
  1,
  datetime.datetime(2008, 11, 22, 14, 10, 46),
  datetime.datetime(2008, 11, 22, 14, 10, 46)),),
    delete_ids = [1]
)
