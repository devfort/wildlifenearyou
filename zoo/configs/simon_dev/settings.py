from zoo.configs.common_settings import *

# Debug settings - turn OFF before launch
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Database settings
DATABASE_NAME = 'zoo_alpha_dev'
DATABASE_USER = 'root'

MEDIA_ROOT = '/srv/django-apps/dev.wildlifenearyou.com/uploaded'

# Xapian settings
SEARCH_ENABLED = True
XAPIAN_BASE_URL = 'http://localhost:9876/search/'
XAPIAN_PERSONAL_PREFIX = 'zoo_alpha_dev'
XAPIAN_LOCATION_DB = '%s_locations' % XAPIAN_PERSONAL_PREFIX
XAPIAN_SPECIES_DB = '%s_species' % XAPIAN_PERSONAL_PREFIX

# SMTP settings
DEFAULT_FROM_EMAIL = 'simon@simonwillison.net'
EMAIL_FROM = DEFAULT_FROM_EMAIL
EMAIL_HOST = 'mail.authsmtp.com'
EMAIL_HOST_USER = 'ac35086'
EMAIL_HOST_PASSWORD = 'xzaf8gbxm'

# Prelaunch middleware
#PRELAUNCH_PASSWORD = 'tigers'
#if PRELAUNCH_PASSWORD:
#    MIDDLEWARE_CLASSES += [
#        'zoo.common.prelaunch_middleware.PreLaunchMiddleware',
#    ]

# API Keys
GOOGLE_MAPS_API_KEY = "ABQIAAAAyYu8a7AdbfUctK3zwwu_2hQ01HQsC4mkjJr7qTVEDPk4sSFdohRgeCFcjXUtZnEU307E9xnV8VU7vw"
FLICKR_API_KEY = '9b42140530b4e1d535adc4b5992bd879'
FLICKR_API_SECRET = '19db0ec3fb0c4e69'

# Dev status bar HTML
DEV_STATUS_HTML = """
<div class="dev-status alpha">
 <p>This is <strong>alpha</strong>.wildlifenearyou.com - please don't link to or Twitter this yet, we're still fixing up some loose ends</p>
</div>
"""

GOOGLE_ANALYTICS_CODE = """
<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-6697903-1");
pageTracker._trackPageview();
} catch(err) {}</script>
"""

HTTP_PORT = 80
