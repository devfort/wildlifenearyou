from django.core import serializers
from django.template import loader, Context
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

from zoo.shortcuts import render
from zoo.animals.models import Species, SuperSpecies
from zoo.favourites.models import FavouriteSpecies

def species(request, slug):
    try:
        species = Species.objects.get(slug=slug)
    except Species.DoesNotExist:
        # eggs
        species = get_object_or_404(SuperSpecies, slug=slug)
        t = loader.get_template('species/%s.html' % species.type)
        c = Context({'species': species})
        return HttpResponse(t.render(c), status=species.status)

    favourites = species.favourited.count()
    hit_parade = 0
    try:
        hit_parade = FavouriteSpecies.hit_parade().index(species) + 1
    except ValueError, e:
        pass

    return render(request, 'species/species.html', {
        'species': species,
        'favourited': species.has_favourited(request.user),
        'hit_parade': hit_parade,
        'favourites': favourites,
    })

def all_species(request):
    return render(request, 'species/all_species.html', {
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
    return render(request, 'species/all_species_latin.html', {
        'all_species': Species.objects.all().order_by('latin_name'),
    })
