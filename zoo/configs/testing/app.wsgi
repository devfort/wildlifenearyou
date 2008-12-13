import os, sys

# Get rid of 'sys.stdout access restricted by mod_wsgi' error
sys.stdout = sys.stderr

# Uses exact same code as alpha.wildlifenearyou.com (at least for the moment)
paths = (
    '/home/simon/sites/alpha.wildlifenearyou.com/zoo/ext',
    '/home/simon/sites/alpha.wildlifenearyou.com/zoo',
    '/home/simon/sites/alpha.wildlifenearyou.com',
)
for path in paths:
    if not path in sys.path:
        sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'zoo.configs.testing.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
