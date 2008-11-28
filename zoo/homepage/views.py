from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseServerError
from zoo.shortcuts import render

from zoo.places.models import Place
from zoo.accounts.forms import RegistrationForm
from zoo.animals.models import Species
from zoo.trips.models import Sighting
from zoo.accounts.models import Profile
from zoo.photos.models import Photo
from zoo.utils import location_from_request

def landing(request):
    places_with_sightings = Place.objects.filter(sighting__isnull=False)
    if places_with_sightings.count():
        random_zoo = places_with_sightings.order_by('?')[0]
    else:
        random_zoo = None

    reg_form = RegistrationForm()

    recent_sightings = Sighting.objects.order_by('-created_at')
    if request.user:
        favourite_animals = Species.objects.filter(favourited=request.user)
        recent_sightings_favourites = Sighting.objects.filter(species__in=favourite_animals).order_by('-created_at')

    featured = {}

    # Doing it this way means the page survives with 0 or >1 featured
    # sites.
    places = Place.objects.filter(featured=True)
    featured['place'] = places.count() > 0 and places[0] or None

    species = Species.objects.filter(featured=True)
    featured['species'] = species.count() > 0 and species[0] or None

    profiles = Profile.objects.filter(featured=True)
    featured['profile'] = profiles.count() > 0 and profiles[0] or None

    num_of_places = Place.objects.count()

    if featured['place']:
        # Have to do this as django template method calls can't take params.
        featured['place'].species = featured['place'].get_species(limit=10)

    if featured['species']:
        location, (lat, lon) = location_from_request(request)
        from zoo.search import nearest_places_with_species as npws
        nearest_species = npws(featured['species'].common_name, (lat, lon))
        if nearest_species:
            featured['species'].nearest = nearest_species[0]

    return render(request, 'homepage/landing.html', {
        'random_zoo': random_zoo,
        'featured': featured,
        'num_of_places': num_of_places,
        'reg_form': reg_form,
        'recent_sightings': recent_sightings,
        'recent_sightings_favourites': recent_sightings_favourites,
    })
