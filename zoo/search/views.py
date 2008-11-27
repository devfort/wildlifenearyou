from zoo.shortcuts import render
from zoo.search import search_places

def search(request):
    q = request.GET.get('q', '')
    results = None
    if q:
        results = search_places(q)
    
    return render(request, 'search/search.html', {
        'q': q,
        'results': results,
    })
