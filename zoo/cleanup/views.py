from zoo.shortcuts import render
from zoo.places.models import Place
from models import PlaceNeedsCleanup

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden, \
    HttpResponse
from django.shortcuts import get_object_or_404

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

@login_required
def merge_places(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        results = Place.objects.filter(known_as__icontains = q)
    
    message = ''
    selected = request.GET.getlist('merge')
    if len(selected) == 2:
        return HttpResponseRedirect('/cleanup/merge-places/%s/%s/' % tuple(
            selected
        ))
    elif len(selected):
        message = 'Please select exactly two items to merge'
    
    return render(request, 'cleanup/merge_places.html', {
        'q': q,
        'results': results,
        'message': message,
    })

@login_required
def confirm_merge_places(request, slug1, slug2):
    place1 = get_object_or_404(Place, pk = slug1)
    place2 = get_object_or_404(Place, pk = slug2)
    
    if request.method == 'POST':
        keep = int(request.POST.get('keep', '0'))
        if keep not in (place1.pk, place1.pk):
            return HttpResponse('You did not select a place to keep')
        
        to_keep = Place.objects.get(pk = keep)
        to_delete = [p for p in (place1, place2) if p.pk != keep]
        assert False, ('keep: ', to_keep, 'delete: ', to_delete)
        # First, save the new details from the form
        for key in request.POST:
            if key != 'keep':
                setattr(to_keep, key, request.POST[key])
        to_keep.save()
        # Next, merge comments from to_delete over to to_keep
        
    
    fields_to_display1 = []
    fields_to_display2 = []
    for field in (
        'known_as', 'legal_name', 'phone', 'url', 'address_line_1',
        'address_line_2', 'town', 'state', 'zip', 'latitude', 'longitude',
        'zoom_level'
    ):
        fields_to_display1.append({
            'name': field,
            'value': getattr(place1, field, ''),
        })
        fields_to_display2.append({
            'name': field,
            'value': getattr(place2, field, ''),
        })
    
    return render(request, 'cleanup/confirm_merge_places.html', {
        'place1': place1,
        'place2': place2,
        'fields_to_display1': fields_to_display1,
        'fields_to_display2': fields_to_display2,
    })
