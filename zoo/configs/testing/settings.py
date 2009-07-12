from zoo.configs.common_settings import *

# Debug settings - turn OFF before launch
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Database settings
DATABASE_NAME = 'zoo_testing'
DATABASE_USER = 'zoo_testing'

# Xapian settings
SEARCH_ENABLED = True
XAPIAN_BASE_URL = 'http://superevildevfort.com:8017/search/'
XAPIAN_PERSONAL_PREFIX = 'zoo_testing'
XAPIAN_LOCATION_DB = '%s_locations' % XAPIAN_PERSONAL_PREFIX
XAPIAN_SPECIES_DB = '%s_species' % XAPIAN_PERSONAL_PREFIX

# SMTP settings
DEFAULT_FROM_EMAIL = 'simon@simonwillison.net'
EMAIL_FROM = DEFAULT_FROM_EMAIL
EMAIL_HOST = 'mail.authsmtp.com'
EMAIL_HOST_USER = 'ac35086'
EMAIL_HOST_PASSWORD = 'xzaf8gbxm'

# API Keys
GOOGLE_MAPS_API_KEY = "ABQIAAAAyYu8a7AdbfUctK3zwwu_2hTGub4EDPAvn1yh6P8Pcoj_zzNVuBRgEgIJQIt3MwOjhDuBkM-JeQb4HA"

# Prelaunch middleware
PRELAUNCH_PASSWORD = 'tigers'
if PRELAUNCH_PASSWORD:
    MIDDLEWARE_CLASSES += [
        'zoo.common.prelaunch_middleware.PreLaunchMiddleware',
    ]

# Dev status bar HTML
DEV_STATUS_HTML = """
<div class="dev-status testing">
<p>This is <strong>testing</strong>.wildlifenearyou.com - enter test data here, real data for launch goes on  <a href="http://alpha.wildlifenearyou.com/">alpha.wildlifenearyou.com</a></p>
</div>
"""

GOOGLE_ANALYTICS_CODE = """
<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-6697903-2");
pageTracker._trackPageview();
} catch(err) {}</script>
"""

HTTP_PORT = 80
