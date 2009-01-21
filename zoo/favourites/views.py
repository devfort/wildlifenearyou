from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect as Redirect

from zoo.shortcuts import render

from zoo.animals.models import Species
from zoo.favourites.models import FavouriteSpecies
from zoo.trips.models import Sighting

HIT_PARADE_LENGTH = 20
OBSCURE_LENGTH = 20

def handle_favourite(request, action):
    if action == 'add':
        return add_favourite(request)
    if action == 'remove':
        return remove_favourite(request)

def add_favourite(request):
    if not request.method == 'POST':
        raise Http404
    slug = request.POST.get('species', None)
    species = get_object_or_404(Species, slug=slug)
    FavouriteSpecies.objects.create(user=request.user,
                                    species=species)

    next = request.POST.get('next', species.urls.absolute)
    return Redirect(next)

def remove_favourite(request):
    if not request.method == 'POST':
        raise Http404
    slug = request.POST.get('species', None)
    species = get_object_or_404(Species, slug=slug)
    try:
        FavouriteSpecies.objects.get(user=request.user,
                                     species=species).delete()
    except FavouriteSpecies.DoesNotExist:
        # Trying to remove something that isn't there; ignore.
        pass

    next = request.POST.get('next', species.urls.absolute)
    return Redirect(next)

def hit_parade(request):
    species_list = FavouriteSpecies.hit_parade()
    species_list = species_list[:HIT_PARADE_LENGTH]

    sightings = Sighting.objects.all()
    obscure = {}
    for s in sightings:
        if s.species:
            obscure[s.species] = obscure.get(s.species, 0) + 1

    obscure_list = obscure.keys()
    for idx in range(len(obscure_list)-1, -1, -1):
        if obscure_list[idx] in species_list:
            del obscure_list[idx]

    for s in obscure_list:
        s.count = obscure[s]

    obscure_list.sort(key=lambda s: s.count)
    obscure_list = obscure_list[:OBSCURE_LENGTH]

    return render(request, 'favourites/hit_parade.html', {
        'species_list': species_list,
        'obscure_species': obscure_list,
    })
