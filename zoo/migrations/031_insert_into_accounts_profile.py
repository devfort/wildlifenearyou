from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m
import datetime

from zoo.accounts.models import Profile
from django.contrib.auth.models import User

user_ids = list(User.objects.values_list('id', flat=True))
profile_user_ids = list(Profile.objects.values_list('user', flat=True))
profile_ids = list(Profile.objects.values_list('id', flat=True))

to_create = sorted(set(user_ids) - set(profile_user_ids))

migration = m.InsertRows(
    table_name = 'accounts_profile',
    columns = [u'user_id'],
    insert_rows = [(uid,) for uid in to_create],
    delete_ids = profile_ids,
)
