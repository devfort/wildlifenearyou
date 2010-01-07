from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect as Redirect, Http404, \
    HttpResponseForbidden

from zoo.shortcuts import render

from zoo.animals.models import Species
from zoo.favourites.models import FavouriteSpecies
from zoo.trips.models import Sighting

HIT_PARADE_LENGTH = 20
OBSCURE_LENGTH = 20

class FavouriteView(object):
    def __init__(self, favourite_class, favourite_attr, model_class):
        self.favourite_class = favourite_class
        self.favourite_attr = favourite_attr
        self.model_class = model_class
    
    def __call__(self, request, action, pk):
        if not request.user or request.user.is_anonymous():
            raise HttpResponseForbidden
        obj = get_object_or_404(self.model_class, pk = pk)
        if action == 'add':
            return self.add(request, obj)
        elif action == 'remove':
            return self.remove(request, obj)
        else:
            raise Http404
    
    def add(self, request, obj):
        self.favourite_class.objects.get_or_create(**{
            'user': request.user,
            self.favourite_attr: obj
        })
        next = request.POST.get('next', obj.get_absolute_url())
        return Redirect(next)
    
    def remove(self, request, obj):
        try:
            self.favourite_class.objects.get(**{
                'user': request.user,
                self.favourite_attr: obj
            }).delete()
        except self.favourite_class.DoesNotExist:
            # Trying to remove something that isn't there; ignore.
            pass
        next = request.POST.get('next', obj.get_absolute_url())
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
