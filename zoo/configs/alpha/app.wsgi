import os, sys, site

ROOT = '/srv/django-apps/staging.wildlifenearyou.com/'

site.addsitedir(ROOT + 'venv/lib/python2.6/site-packages')

# Get rid of 'sys.stdout access restricted by mod_wsgi' error
sys.stdout = sys.stderr

paths = (
    ROOT + 'current/zoo/ext',
    ROOT + 'current/zoo',
    ROOT + 'current',
)
for path in paths:
    if not path in sys.path:
        sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'zoo.configs.alpha.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
