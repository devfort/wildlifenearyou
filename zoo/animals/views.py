from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseServerError
from django.core import serializers
from django.template import loader, Context

from zoo.animals.models import Species
from zoo.shortcuts import render

def species(request, slug):
    species = get_object_or_404(Species, slug=slug)
    return render(request, 'species/species.html', {
        'species': species,
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
    species = get_object_or_404(Species, latin_name=latin_name)
    return HttpResponseRedirect(species.urls.absolute)

def all_species_latin(request):
    return render(request, 'species/all_species_latin.html', {
        'all_species': Species.objects.all().order_by('latin_name'),
    })

def narwhals(request):
    return render(request, 'species/narwhals.html', {})

def extinct(request):
    t = loader.get_template('species/extinct.html')
    c = Context()
    return HttpResponse(t.render(c), status=410) # Gone

def imaginary(request, animal):
    t = loader.get_template('species/imaginary.html')
    c = Context()
    return HttpResponse(t.render(c), status=417) # Expectation failed

