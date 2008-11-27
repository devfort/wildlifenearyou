from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseServerError
from zoo.shortcuts import render

from zoo.places.models import Place
from zoo.accounts.forms import RegistrationForm
from zoo.animals.models import Species
from zoo.accounts.models import Profile
from zoo.photos.models import Photo

def landing(request):
    places_with_sightings = Place.objects.filter(sighting__isnull=False)
    if places_with_sightings.count():
        random_zoo = places_with_sightings.order_by('?')[0]
    else:
        random_zoo = None

    reg_form = RegistrationForm()

    featured = {}

    # Doing it this way means the page survives with 0 or >1 featured
    # sites.
    places = Place.objects.filter(featured=True)
    featured['place'] = places.count() > 0 and places[0] or None

    species = Species.objects.filter(featured=True)
    featured['species'] = species.count() > 0 and species[0] or None

    profiles = Profile.objects.filter(featured=True)
    featured['profile'] = profiles.count() > 0 and profiles[0] or None


    if featured['place']:
        # Have to do this as django template method calls can't take params.
        featured['place'].species = featured['place'].get_species(limit=10)

    return render(request, 'homepage/landing.html', {
        'random_zoo': random_zoo,
        'featured': featured,
        'reg_form': reg_form,
    })
