from django.conf import settings
from django.utils import simplejson
import flickrapi

top = 'jsonFlickrApi('
tail = ')'
def parse_json(rest_json):
    '''Parses a JSON response from Flickr into a Python dictionary.'''
    # First strip the jsonFlickrApi( and trailing )
    rest_json = rest_json.strip()
    if rest_json.startswith(top):
        rest_json = rest_json[len(top):]
    
    if rest_json.endswith(tail):
        rest_json = rest_json[:-len(tail)]
    
    json = simplejson.loads(rest_json)
    
    if json['stat'] == 'ok' or not self.fail_on_error:
        if 'photos' in json and 'photo' in json['photos']:
            annotate_photos(json['photos']['photo'])
        # Ditto for photo sets, which include details of their primary photo
        if 'photosets' in json and 'photoset' in json['photosets']:
            annotate_photos(json['photosets']['photoset'])
        
        return json
    
    err = json.err[0]
    raise flickrapi.FlickrError(u'Error: %(code)s: %(msg)s' % err)

# http://www.flickr.com/services/api/misc.urls.html
FLICKR_URL_TEMPLATE = \
    'http://farm%(farm)s.static.flickr.com/%(server)s/%(photo_id)s_%(secret)s'

FLICKR_FORMATS = {
    u'square': u'_s.jpg', # 75x75
    u'thumbnail': u'_t.jpg', # 100 on longest side
    u'small': u'_m.jpg', # 240 on longest side
    u'medium': u'.jpg', # 500 on longest side
    u'large': u'_b.jpg', # 1024 on longest side
}
FLICKR_PHOTO_URL = u'http://www.flickr.com/photos.gne?id=%(id)s'

def annotate_photos(json_photos):
    "Annotate a list of Flickr photo dicts with useful URLs"
    for photo in json_photos:
        # in photosets 'primary' is the photo ID, otherwise it's just 'id'
        photo['photo_id'] = photo.get('primary', photo['id'])
        base_url = FLICKR_URL_TEMPLATE % photo
        for format, suffix in FLICKR_FORMATS.items():
            photo[format] = base_url + suffix
        photo[u'url'] = FLICKR_PHOTO_URL % photo
        
        # Anything that has a single _content item should be flattened
        # e.g. "description": {"_content": "..."} as seen on photoset JSON
        for key, value in photo.items():
            if isinstance(value, dict) and len(value.keys()) == 1 and \
                value.keys()[0] == '_content':
                photo[key] = value.values()[0]

class BetterFlickrAPI(flickrapi.FlickrAPI):
    def _FlickrAPI__wrap_in_parser(self, *args, **kwargs):
        # We do our JSON decoding here - there doesn't appear to be a more 
        # elegant hook for it (the rest_parsers dictionary doesn't work 
        # because it forces the format argument sent over to Flickr to be 
        # 'rest' instead of 'json')
        data = flickrapi.FlickrAPI._FlickrAPI__wrap_in_parser(
            self, *args, **kwargs
        )
        if not isinstance(data, basestring):
            return data # Probably an XMLNode, used by the auth methods
        return parse_json(data)

def Flickr(**kwargs):
    return BetterFlickrAPI(
        settings.FLICKR_API_KEY, settings.FLICKR_API_SECRET, format='json',
        **kwargs
    )
