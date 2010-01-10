# Settings for use in local development - see zoo.configs for production
from zoo.configs.common_settings import *

DEBUG = True
TEMPLATE_DEBUG = True

DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'sedf'
DATABASE_USER = 'sedf'

# run "python -m smtpd -n -c DebuggingServer localhost:1025" to see outgoing
# messages dumped to the terminal
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

SECRET_KEY = '6p-br^04irwt=+&4dag12(-7_!p4&t=u+h1+#$xrvr0n6=+o^d'

#CACHE_BACKEND = 'db://django_cache'

try:
    import debug_toolbar
    MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INSTALLED_APPS.append('debug_toolbar')
except ImportError:
    pass

MIDDLEWARE_CLASSES.append('debug_footer.DebugFooter')

EMAIL_FROM = 'zoo@example.com'

# This API key is for http://localhost - over-ride it in local_settings.py
GOOGLE_MAPS_API_KEY = 'ABQIAAAAyYu8a7AdbfUctK3zwwu_2hT2yXp_ZAY8_ufC3CFXhHIE1NvwkxSvLcMTOAnq4jYs9Ef-8-uu97vUrA'
# TODO: If we ever put ads on the site, apply for a "Commercial" Flickr key
FLICKR_API_KEY = '940756abbc65d6f8223f3b9494d0b19f'
FLICKR_API_SECRET = '5c121cb53d477871'

# SEARCH_ENABLED should be turned on only when a Xapian server is available.
SEARCH_ENABLED = True

XAPIAN_BASE_URL = 'http://superevildevfort.com:8017/search/'
XAPIAN_LOCATION_DB = 'locations' # It's safe to share the locations DB

XAPIAN_PERSONAL_PREFIX = ''
try:
    from local_settings import *
except ImportError:
    pass

assert XAPIAN_PERSONAL_PREFIX, """
    You need to create a XAPIAN_PERSONAL_PREFIX setting in your
    local_settings.py file - it should be your username. This will be used for
    search index files created on our shared search web service server, but
    because these indexes will reference your local Django database IDs it's
    important that you don't end up talking to someone else's search index.
"""

# Everyone needs their own species index, since once we create a local
# record of a species in the animal_species table we write the ID from that
# record back to the search index.
XAPIAN_SPECIES_DB = '%s_species' % XAPIAN_PERSONAL_PREFIX

DEV_STATUS_HTML = """
<div class="dev-status localhost">
	<p>This is <a href="/">a local instance</a> - you can enter real data 
	at <a href="http://alpha.wildlifenearyou.com/">alpha.wildlifenearyou.com</a></p>
</div>
"""
