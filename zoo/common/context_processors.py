from django.core.cache import cache
from django.conf import settings
from django.utils.safestring import mark_safe

from zoo.animals.models import Species
from zoo.utils import location_from_request
from zoo.search import nearest_places_with_species
from zoo.accounts.openid import endpoint as openid_endpoint

from random import randint

def standard(request):
    num_species = cache.get('total_num_of_species')
    if not num_species:
        num_species = Species.objects.all().count()
        cache.set('total_num_of_species', num_species, 60)

    return {
        'base': 'base.html',
        'total_num_of_species': num_species,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
        'dev_status_html': mark_safe(settings.DEV_STATUS_HTML),
        'GOOGLE_ANALYTICS_CODE': mark_safe(settings.GOOGLE_ANALYTICS_CODE),
        'login_next': openid_endpoint.sign_next(request.get_full_path()),
    }
