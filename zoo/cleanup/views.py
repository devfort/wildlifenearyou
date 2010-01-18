from zoo.shortcuts import render
from zoo.places.models import Place
from models import PlaceNeedsCleanup

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden

@login_required
def cleanup_places(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    
    done = []
    if request.POST:
        for key in request.POST.keys():
            if key.endswith('lat'):
                lat = float(request.POST[key])
                lon = float(request.POST[key.replace('lat', 'lon')])
                pk = key.split('_')[1]
                place = Place.objects.get(pk = pk)
                place.latitude = lat
                place.longitude = lon
                place.save()
                PlaceNeedsCleanup.objects.filter(place = place).delete()
                done.append(place)
    
    places = PlaceNeedsCleanup.objects.select_related(
        'place'
    )
    reverse = ('reverse' in request.REQUEST)
    if reverse:
        places = places.order_by('-pk')
    else:
        places = places.order_by('pk')
        
    return render(request, 'cleanup/places.html', {
        'places': [p.place for p in places[:10]],
        'done': done,
        'reverse': reverse,
        'total_places': PlaceNeedsCleanup.objects.count(),
    })
