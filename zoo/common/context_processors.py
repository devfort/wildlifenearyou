from django.core.cache import cache
from django.conf import settings

from zoo.animals.models import Species
from zoo.utils import location_from_request
from zoo.search import nearest_places_with_species

from random import randint

def standard(request):
    num_species = cache.get('total_num_of_species')
    if not num_species:
        num_species = Species.objects.all().count()
        cache.set('total_num_of_species', num_species, 60)

    rand = randint(1, 2)
    location, (lat, lon) = location_from_request(request)
    animal = None
    if location and rand==1 and num_species > 0:
        animal = cache.get('footer_stat_nearest_%s' % location)
        if not animal:
            random_animal = Species.objects.order_by('?')[0]
            nearest = nearest_places_with_species(random_animal.common_name, (lat, lon))
            if nearest:
                animal = {
                    'name': random_animal.common_name,
                    'url': random_animal.urls.absolute,
                    'dist': int(nearest[0].distance_miles+0.5),
                    'place_url': nearest[0].urls.absolute,
                    'place_name': nearest[0],
                }
                cache.set('footer_stat_nearest_%s' % location, animal, 300)

    if animal is None:
        rand = 2

    return {'base': 'base.html',
            'total_num_of_species': num_species,
            'rand': rand,
            'random_animal': animal,
            'location': location,
            'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
    }
