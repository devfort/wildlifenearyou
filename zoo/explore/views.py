from zoo.shortcuts import render
from zoo.photos.models import Photo
from zoo.trips.models import Trip

def index(request):
    context = {
        'photos': Photo.objects.filter(
            is_visible = True
        ).select_related('created_by').order_by('-created_at')[:16],
        'recent_trips': Trip.objects.select_related(
            'created_by', 'place', 'place__country'
        ).order_by('-created_at')[:10],
    }
    if not request.user.is_anonymous():
        context['is_logged_in'] = True
        context['photos_of_your_favourites'] = Photo.objects.filter(
            is_visible = True
        ).filter(
            sightings__species__favourited__user = request.user
        ).select_related('created_by').order_by('-created_at')[:16]
        context['trips_to_places_you_have_been'] = Trip.objects.filter(
            place__trip__created_by = request.user
        ).exclude(
            created_by = request.user
        ).select_related(
            'created_by', 'place', 'place__country'
        ).order_by('-created_at')[:10]
        context['favourite_species'] = request.user.\
            favourite_species.select_related('species')
    
    return render(request, 'explore/index.html', context)
