from zoo.shortcuts import render
from django.shortcuts import get_object_or_404
from models import List
from animals.models import Species
from trips.add_trip import species_for_freebase_details
from trips.add_trip_utils import search
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponseForbidden

def index(request):
    return render(request, 'lists/lists.html', {
        'lists': List.objects.all(),
    })

def view_list(request, slug):
    l = get_object_or_404(List, slug = slug)
    top_spotters = User.objects.filter(
        created_sighting_set__species__list = l
    ).annotate(
        num_spotted = Count('created_sighting_set__species', distinct = True)
    ).order_by('-num_spotted')[:5]
    species = l.species.all().order_by('common_name')
    if not request.user.is_anonymous():
        # Annotate species list with which ones they have seen
        species_seen = set([
            s.pk for s in request.user.get_profile().passport().seen_species
        ])
        for s in species:
            if s.pk in species_seen:
                s.seen_by_you = True
    
    return render(request, 'lists/list.html', {
        'list': l,
        'top_spotters': top_spotters,
        'species': species,
    })

def edit(request, slug):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    l = get_object_or_404(List, slug = slug)
    not_found = []
    if request.method == 'POST':
        freebase_ids = request.POST.getlist('freebase_id')
        for id in freebase_ids:
            id = id.replace('#', '').strip()
            if not id:
                continue
            species = None
            matches = Species.objects.filter(freebase_id = '/guid/%s' % id)
            if matches:
                species = matches[0]
            else:
                search_results = search(id)
                if search_results:
                    species = species_for_freebase_details(search_results[0])
                else:
                    not_found.append(id)
                    continue
            l.species.add(species)
    
    return render(request, 'lists/edit.html', {
        'l': l,
        'not_found': not_found,
        'range_100': range(100)
    })
