import sys
import site
import os

sys.stdout = sys.stderr # Avoid 'sys.stdout access restricted by mod_wsgi'

prev_sys_path = list(sys.path)

# add the site-packages of our virtualenv as a site dir
site.addsitedir(
  '/srv/django-apps/dev.wildlifenearyou.com/venv/lib/python2.5/site-packages'
)

# Add a few more required directories to the python path
paths = (
    '/srv/django-apps/dev.wildlifenearyou.com/current/zoo/ext',
    '/srv/django-apps/dev.wildlifenearyou.com/current/zoo/',
    '/srv/django-apps/dev.wildlifenearyou.com/current',
)
for path in paths:
    if not path in sys.path:
        sys.path.insert(0, path)

# reorder sys.path so new directories from the addsitedir show up first
new_sys_path = [p for p in sys.path if p not in prev_sys_path]
for item in new_sys_path:
    sys.path.remove(item)
sys.path[:0] = new_sys_path

from django.core.handlers.wsgi import WSGIHandler
os.environ['DJANGO_SETTINGS_MODULE'] = 'zoo.configs.simon_dev.settings'
application = WSGIHandler()
