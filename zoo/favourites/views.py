from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect as Redirect

from zoo.shortcuts import render

from zoo.animals.models import Species
from zoo.favourites.models import FavouriteSpecies

HIT_PARADE_LENGTH = 10

def handle_favourite(request, action):
    if action == 'add':
        return add_favourite(request)
    if action == 'remove':
        return remove_favourite(request)

def add_favourite(request):
    if not request.POST:
        raise Http404
    slug = request.POST.get('species', None)
    species = get_object_or_404(Species, slug=slug)
    FavouriteSpecies.objects.create(user=request.user,
                                    species=species)

    next = request.POST.get('next', species.urls.absolute)
    return Redirect(next)

def remove_favourite(request):
    if not request.POST:
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
    all_favourites = FavouriteSpecies.objects.all()
    species = {}
    for f in all_favourites:
        species[f.species] = species.get(f.species, 0) + 1

    species_list = species.keys()
    for s in species_list:
        s.count = species[s]

    species_list.sort(key=lambda s: s.count, reverse=True)
    species_list = species_list[:HIT_PARADE_LENGTH]

    return render(request, 'favourites/hit_parade.html', {
        'species_list': species_list,
    })
