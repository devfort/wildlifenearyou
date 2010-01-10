from django.http import HttpResponse, HttpResponseRedirect, Http404, \
    HttpResponseServerError
from zoo.shortcuts import render
from django.conf import settings

from zoo.places.models import Place, Country
from zoo.accounts.forms import RegistrationForm
from zoo.animals.models import Species
from zoo.trips.models import Sighting, Trip
from zoo.accounts.models import Profile
from zoo.photos.models import Photo
from zoo.utils import location_from_request

from basic.blog.models import Post

def homepage(request):

    reg_form = RegistrationForm()

    recent_sightings = Sighting.objects.order_by('-created_at')
    recent_sightings_favourites = None
    if request.user.is_authenticated():
        favourite_animals = Species.objects.filter(favourited=request.user)
        recent_sightings_favourites = Sighting.objects.filter(
            species__in=favourite_animals
        ).order_by('-created_at')

    featured = {}

    # Doing it this way means the page survives with 0 or >1 featured
    # sites.
    places = Place.objects.filter(featured=True).order_by('?')
    featured['place'] = places.count() > 0 and places[0] or None

    species = Species.objects.filter(featured=True).order_by('?')
    featured['species'] = species.count() > 0 and species[0] or None

    profiles = Profile.objects.filter(featured=True).order_by('?')
    featured['profile'] = profiles.count() > 0 and profiles[0] or None

    num_of_places = Place.objects.count()
    num_of_countries = Country.objects.filter(
        place__isnull = False
    ).distinct().count()

    if featured['place']:
        # Have to do this as django template method calls can't take params.
        try:
            featured['place'].species = featured['place'].get_species(
                limit=10
            )
        except Species.DoesNotExist:
            featured['place'].species = None

    if featured['species']:
        location, (lat, lon) = location_from_request(request)
        if (lat, lon) != (None, None):
            from zoo.search import nearest_places_with_species as npws
            nearest_species = npws(
                featured['species'].common_name, (lat, lon)
            )
            if nearest_species:
                featured['species'].nearest = nearest_species[0]
    
    if settings.SEARCH_ENABLED:
        default_search = ''
    else:
        default_search = 'SEARCH CURRENTLY DISABLED'
    
    return render(request, 'homepage.html', {
        'featured': featured,
        'num_of_places': num_of_places,
        'num_of_countries': num_of_countries,
        'reg_form': reg_form,
        'recent_sightings': recent_sightings,
        'recent_sightings_favourites': recent_sightings_favourites,
        'default_search': default_search,
        'recent_photos': Photo.objects.filter(
            is_visible = True
        ).order_by('-created_at')[:20],
        'recent_trips': Trip.objects.order_by('-created_at')[:5],
        'blog_posts': Post.objects.published(),
#        'recent_trips': Trip.objects.filter(
#            start__isnull=False
#        ).order_by('-start')[:5]
    })
