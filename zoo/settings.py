# Django settings for zoo project.

import os
OUR_ROOT = os.path.realpath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'sedf'             # Or path to database file if using sqlite3.
DATABASE_USER = 'sedf'             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(OUR_ROOT, 'static/uploaded')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/uploaded/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '6p-br^04irwt=+&4dag12(-7_!p4&t=u+h1+#$xrvr0n6=+o^d'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'zoo.middleware.OnlyLowercaseUrls',
    'zoo.middleware.AutoCreatedAndModifiedFields',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]
PRELAUNCH_PASSWORD = 'tigers'


ROOT_URLCONF = 'zoo.urls'

AUTHENTICATION_BACKENDS = (
    'accounts.backends.ModelBackend',
)
AUTH_PROFILE_MODULE = 'accounts.profile'
LOGIN_REDIRECT_URL = '/profile/'
LOGIN_URL = '/login/'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(OUR_ROOT, 'templates'),
    os.path.join(OUR_ROOT, 'ext/django/contrib/databrowse/templates'),
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.auth',
    'zoo.context_processors.standard',
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.admin',
    'django.contrib.humanize',
    'dmigrations', # from zoo.ext
    'zoo.accounts',
    'zoo.animals',
    'zoo.places',
    'zoo.changerequests',
    'zoo.homepage',
    'zoo.faces',
    'zoo.geonames',
    'sorl.thumbnail', # from zoo.ext
    'zoo.photos',
    'zoo.trips',
    'zoo.favourites',
    'django.contrib.comments',
    'schedule', # from zoo.ext
    'zoo.feedback',
    'zoo.freebase',
    'zoo.search',
]

DMIGRATIONS_DIR = os.path.join(OUR_ROOT, 'migrations')

CACHE_BACKEND = 'dummy:///'

INTERNAL_IPS = ('127.0.0.1',)

try:
    import debug_toolbar
    MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INSTALLED_APPS.append('debug_toolbar')
except ImportError:
    pass

EMAIL_FROM = 'zoo@example.com'

# This API key is for http://localhost - over-ride it in local_settings.py
GOOGLE_MAPS_API_KEY = 'ABQIAAAAyYu8a7AdbfUctK3zwwu_2hT2yXp_ZAY8_ufC3CFXhHIE1NvwkxSvLcMTOAnq4jYs9Ef-8-uu97vUrA'

# SEARCH_ENABLED should be turned on only when a Xapian server is available.
SEARCH_ENABLED = False

XAPIAN_BASE_URL = 'http://superevildevfort.com:8017/search/'
XAPIAN_LOCATION_DB = 'locations' # It's safe to share the locations DB

XAPIAN_PERSONAL_PREFIX = ''
try:
    from local_settings import *
except ImportError:
    pass

if PRELAUNCH_PASSWORD:
    MIDDLEWARE_CLASSES += ['zoo.prelaunch_middleware.PreLaunchMiddleware',]

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


#----------------------------------------------------------------------------------------------
#                                                                                             -
#  #                                                                                          -
#  #                                                                                          -
#  #         ########                                                                         -
#  #        ##      #  #                                                                      -
#  #        #       #  #                                                                      -
#  #        #      ##  #         ##########                                                   -
#  #        ########   #        # #       ###                         #                       -
#  ####                #        ###         ##      #       ##       ##                       -
#                      #         ##          #    ## ###   # ##     ##                        -
#                      #####     ##          #    #    ##  #   ##  #      ####         #####  -
#                                 #         #     #     #  #    #  #    ##            ##      -
#                                 #      ###      #######  #     # #   ##            #        -
#                                #########                        ##  ##   ##        #        -
#                                                                 ## #      ####     ##       -
#                                                                  ##          #      #       -
#                                                                    ##########       #       -
#                                       ##      #####                           ######        -
#                                        ###                                                  -
#         ##############                                                                      -
#        ##            ###                                                                    -
#       ##    ###    ### #                    #####                                           -
#       #       #    # # #                 ####   ####                                        -
#       ##   ##          #                 #         #                                        -
#        #      #####    #                 ####    ##                                         -
#         ####      # # ##                    #####                                           -
#            ###########                                                                      -
#                                                                                             -
#----------------------------------------------------------------------------------------------
