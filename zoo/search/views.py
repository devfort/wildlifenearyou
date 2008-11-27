from zoo.shortcuts import render
from zoo.search import search_places, search_known_species
from pprint import pformat

def search(request):
    q = request.GET.get('q', '')
    results = None
    species_results = None
    if q:
        results, results_info = search_places(q, details=True)
        species_results, species_results_info = search_known_species(
            ' OR '.join(q.split()), details=True
        )
        # Annotate results with a special species list that has a flag on 
        # any species which came up in the species results as well
        for result in results:
            result.species_list = result.get_species()
            for species in result.species_list:
                if species in species_results:
                    species.matches_search = True
        
    return render(request, 'search/search.html', {
        'q': q,
        'results': results,
        'results_info': pformat(results_info),
        'species_results': species_results,
        'species_results_info': pformat(species_results_info),
    })
