# Common settings. These should be things that define the application itself,
# rather than things that may change for different environments.

import os
OUR_ROOT = os.path.join(os.path.realpath(os.path.dirname(__file__)), '..')

DEBUG = False
TEMPLATE_DEBUG = False

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'
DATABASE_NAME = ''
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

CACHE_BACKEND = 'file:///tmp/wildlifenearyou_cache'

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

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = [
    'common.wsgi_error_middleware.WsgiLogErrors',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'zoo.invitereg.middleware.InviteOnlyMiddleware',        
    'zoo.common.middleware.AutoCreatedAndModifiedFields',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django_openid.registration.RegistrationConsumer',
    'zoo.common.middleware.Custom403',
    'pagination.middleware.PaginationMiddleware',
]

ROOT_URLCONF = 'zoo.urls'

AUTHENTICATION_BACKENDS = (
    'accounts.backends.ModelBackend',
)
AUTH_PROFILE_MODULE = 'accounts.profile'
LOGIN_REDIRECT_URL = '/profile/'
LOGIN_URL = '/account/login/'

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
    'zoo.common.context_processors.standard',
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
    'zoo.feedback',
    #'zoo.freebase',
    'zoo.search',
    'zoo.common',
    'zoo.launchsignups',
    'django_openid',
    'pagination',
    'zoo.invitereg',
    # The next four items are dependencies for basic.blog
    'basic.blog',
    'basic.inlines',
    'tagging',
    'django.contrib.markup'
]

DMIGRATIONS_DIR = os.path.join(OUR_ROOT, 'migrations')

INTERNAL_IPS = ('127.0.0.1',)

# wildlifenearyou.com/{username} means we need to reserve a lot of namespace
RESERVED_USERNAMES = set(
    """
    feed www help security porn manage smtp fuck pop manager api owner shit 
    secure ftp discussion blog features test mail email administrator 
    xmlrpc web xxx pop3 abuse atom complaints news information imap cunt 
    info pr0n about forum admin weblog team feeds root about info news blog 
    forum features discussion email abuse complaints map tags ajax django 
    comet poll polling thereyet filter search zoom machinetags search 
    people profiles profile person navigate nav browse manage static css 
    javascript js code flags flag country countries region place places 
    photos owner maps upload geocode geocoding login logout openid openids 
    recover lost signup reports report flickr upcoming mashups recent irc 
    group groups bulletin bulletins messages message newsfeed events 
    companies active rss img company books shop sales animals species 
    plants narwhals plant animal wildlife latin dictionary fish zoos zoo 
    aquarium aquariums park parks safari arboretum arboretums autocomplete 
    popular invite debug
    """.strip().split()
)

GOOGLE_MAPS_API_KEY = ''
GOOGLE_ANALYTICS_CODE = ''
GOOGLE_GEOCODE_API_KEY = 'wildlifenearyou.com'
# Registered by simonwillison, for www.wildlifenearyou.com
PLACEMAKER_API_KEY = \
    'dElrnn3V34EGmyfAgIpBKYa9m35k00NrPz_WyOifWUKfBeCX91hrRA6IPV6o1_X9KrY2Jg--'

# Used solely to display to the user what the file upload limit is;
# this is actually set in nginx configuration. In bytes.
FILE_UPLOAD_SIZE_LIMIT = 2*1024*1024

# Used by zoo.utils.make_absolute_url to get the right netloc.
HTTP_PORT = 8000
