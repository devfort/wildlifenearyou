from django.conf import settings
from django.utils import simplejson
import urllib

def search(q):
    url = settings.XAPIAN_LOCATION_SEARCH_URL + '?' + urllib.urlencode({
        'q': q,
    })
    return simplejson.load(urllib.urlopen(url))
