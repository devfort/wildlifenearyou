from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseServerError
from zoo.shortcuts import render

from zoo.places.models import Place

def landing(request):
    places_with_sightings = Place.objects.filter(sighting__isnull=False)
    if places_with_sightings.count():
        random_zoo = places_with_sightings.order_by('?')[0]
    else:
        random_zoo = None
        
    return render(request, 'homepage/landing.html', {
        'random_zoo': random_zoo,
    })
