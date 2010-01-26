from django.http import HttpResponsePermanentRedirect, Http404
from django.shortcuts import get_object_or_404
from places.models import Place
from trips.models import Trip
from animals.models import Species
from photos.models import Photo
from django.contrib.auth.models import User

from utils import converter

import urlparse

PREFIXES = {
    'p': Place,
    't': Trip,
    's': Species,
    'i': Photo, # 'i' is for image
    'u': User,
}
URL = 'http://www.wildlifenearyou.com/'

def index(request, prefix, code):
    model = PREFIXES.get(prefix, None)
    if not model:
        raise Http404
    try:
        pk = converter.to_int(code)
    except ValueError:
        raise Http404
    obj = get_object_or_404(model, pk = pk)
    path = obj.get_absolute_url()
    return HttpResponsePermanentRedirect(urlparse.urljoin(URL, path))
