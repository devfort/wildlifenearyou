from zoo.shortcuts import render
from zoo.search import search_places, search_known_species, search_near, search_locations
from pprint import pformat
from djape.client import Query

def search(request):
    q = request.GET.get('q', '')
    near = request.GET.get('near', None)
    
    results = None
    species_results = None
    results_info = None
    species_results_info = None
    results_corrected_q = None
    species_results_corrected_q = None
    location_results = None
    
    if q:
        results, results_info, results_corrected_q = \
            search_places(q, details=True, latlon=near)
        species_results, species_results_info, species_results_corrected_q = \
            search_known_species(q, details=True, default_op=Query.OP_OR)
        near_results = search_near('', q)
        location_results = search_locations(q, 3)
        # Annotate results with a special species list that has a flag on 
        # any species which came up in the species results as well
        for result in results:
            result.species_list = result.get_species()
            for species in result.species_list:
                if species in species_results:
                    species.matches_search = True
            # If we got back a distance, bung that on there too
            try:
                result.distance = ([
                    d for d in results_info['items'] 
                    if d['id'] == 'places.Place:%s' % result.id
                ][0]['geo_distance']['latlon'] / 1609.344)
            except (KeyError, IndexError):
                pass
        
    return render(request, 'search/search.html', {
        'q': q,
        'results': results,
        'results_info': pformat(results_info),
        'results_corrected_q': results_corrected_q,
        'species_results': species_results,
        'species_results_info': pformat(species_results_info),
        'species_results_corrected_q': species_results_corrected_q,
        'location_results': location_results,
    })

from zoo.shortcuts import render_json
from zoo.search import search_locations
def location_complete(request):
    q = request.GET.get('q', '')
    results = search_locations(q)
    return render_json(request, list(results))
