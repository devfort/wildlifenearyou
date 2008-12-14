from zoo.configs.common_settings import *

# Debug settings - turn OFF before launch
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Database settings
DATABASE_NAME = 'zoo_alpha'
DATABASE_USER = 'zoo_alpha'

# Xapian settings
SEARCH_ENABLED = True
XAPIAN_BASE_URL = 'http://superevildevfort.com:8017/search/'
XAPIAN_PERSONAL_PREFIX = 'zoo_alpha'
XAPIAN_LOCATION_DB = '%s_locations' % XAPIAN_PERSONAL_PREFIX
XAPIAN_SPECIES_DB = '%s_species' % XAPIAN_PERSONAL_PREFIX

# SMTP settings
DEFAULT_FROM_EMAIL = 'simon@simonwillison.net'
EMAIL_FROM = DEFAULT_FROM_EMAIL
EMAIL_HOST = 'mail.authsmtp.com'
EMAIL_HOST_USER = 'ac35086'
EMAIL_HOST_PASSWORD = 'xzaf8gbxm'

# Prelaunch middleware
PRELAUNCH_PASSWORD = 'tigers'
if PRELAUNCH_PASSWORD:
    MIDDLEWARE_CLASSES += [
        'zoo.common.prelaunch_middleware.PreLaunchMiddleware',
    ]

# API Keys
GOOGLE_MAPS_API_KEY = "ABQIAAAAyYu8a7AdbfUctK3zwwu_2hQ01HQsC4mkjJr7qTVEDPk4sSFdohRgeCFcjXUtZnEU307E9xnV8VU7vw"

# Dev status bar HTML
DEV_STATUS_HTML = """
<div class="dev-status alpha">
 <p>This is <strong>alpha</strong>.wildlifenearyou.com - please enter only
 REAL data for launch here, use 
 <a href="http://testing.wildlifenearyou.com/">testing.wildlifenearyou.com</a> 
 for testing</p>
</div>
"""
