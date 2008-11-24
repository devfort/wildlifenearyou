from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, \
    HttpResponseServerError
from zoo.shortcuts import render

from zoo.places.models import Place, Country
from zoo.animals.models import Species
from zoo.trips.models import Trip

SPECIES_ON_PLACE_PAGE = 10

def get_place_species(place, user, limit=None):
    passport = Trip.get_passport(user)
    species_list = list(Species.objects.filter(trip__place=place))

    by_count = {}
    for species in species_list:
        by_count[species] = by_count.get(species, 0) + 1

    species_list = by_count.keys()

    for species in species_list:
        species.count = by_count[species]
        if species in passport.seen_species:
            species.seen = True

    species_list.sort(key=lambda s:s.count, reverse=True)

    if limit:
        species_list = species_list[:limit]

    return species_list

def place(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)

    species_list = get_place_species(place, request.user, SPECIES_ON_PLACE_PAGE)

    return render(request, 'places/place.html', {
        'place': place,
        'species_list': species_list,
    })

def place_species(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)

    species_list = get_place_species(place, request.user)

    return render(request, 'places/place_species.html', {
        'place': place,
        'species_list': species_list,
    })


def country(request, country_code):
    country = get_object_or_404(Country, country_code=country_code)
    places = Place.objects.filter(country__country_code=country_code).order_by('known_as')

    return render(request, 'places/country.html', {
        'country': country,
        'places': places,
    })

def all_countries(request):
    return render(request, 'places/all_countries.html', {
        'all_countries': Country.objects.all().order_by('name'),
    })



