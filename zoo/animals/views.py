from django.core import serializers
from django.template import loader, Context
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

from zoo.shortcuts import render
from zoo.animals.models import Species, SuperSpecies
from zoo.favourites.models import FavouriteSpecies

from zoo.search import nearest_places_with_species
from zoo.utils import location_from_request

from django.contrib.auth.models import User

SPOTTERS_ON_SPECIES_PAGE = 5
FAVOURITERS_ON_SPECIES_PAGE = 5

def species(request, slug):
    try:
        species = Species.objects.get(slug=slug)
    except Species.DoesNotExist:
        # eggs
        species = get_object_or_404(SuperSpecies, slug=slug)
        t = loader.get_template('animals/%s.html' % species.type)
        c = Context({'species': species})
        return HttpResponse(t.render(c), status=species.status)
    
    num_favourites = species.favourited.count()
    
    # If we have the user's location, find the nearest animal of this species
    description, (latitude, longitude) = location_from_request(request)
    nearest = None
    if description:
        try:
            nearest = nearest_places_with_species(
                species.common_name, '%f %f' % (latitude, longitude)
            )[0]
        except IndexError:
            nearest = None

    spotters = User.objects.filter(
        created_sighting_set__species = species
    ).distinct()
    return render(request, 'animals/species.html', {
        'species': species,
        'favourited': species.is_favourited_by(request.user),
        'num_favourites': num_favourites,
        'nearest': nearest,
        'location_description': description,
        'spotters': spotters[0:SPOTTERS_ON_SPECIES_PAGE],
        'more_spotters': spotters.count() > SPOTTERS_ON_SPECIES_PAGE,
    })

def species_spotters(request, slug):
    species = get_object_or_404(Species, slug=slug)
    spotters = User.objects.filter(created_sighting_set__species=species).distinct()
    return render(request, 'animals/spotters.html', {
        'species': species,
        'spotters': spotters,
    })

def all_species(request):
    return render(request, 'animals/all_species.html', {
        'all_species': Species.objects.all().order_by('common_name'),
    })

def species_xml(request):
    return HttpResponse(
        serializers.serialize('xml', Species.objects.all()),
        content_type = 'application/xml; charset=utf8'
    )

def species_latin(request, latin_name):
    try:
        species = Species.objects.get(latin_name=latin_name)
    except Species.DoesNotExist:
        # eggs
        species = get_object_or_404(SuperSpecies, latin_name=latin_name)

    return HttpResponseRedirect(species.urls.absolute)

def all_species_latin(request):
    return render(request, 'animals/all_species_latin.html', {
        'all_species': Species.objects.all().order_by('latin_name'),
    })
