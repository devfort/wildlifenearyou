from zoo.shortcuts import Redirect, render_json
from zoo.search import search_locations

def set_location(request):
    response = Redirect('/')
    location = request.POST.get('location', '')
    if location:
        results = search_locations(location)
        if results:
            response.set_cookie(
                'current_location',
                list(results)[0]['latlon'],
                path = '/',
            )
    return response

def autocomplete(request):
    q = request.GET.get('q')
    results = search_locations(q)
    return render_json(request, list(results))
    
    #{
    #    'results': [{
    #        'id': r['search_id'],
    #        'name': r['description'],
    #    } for r in results]
    #})
