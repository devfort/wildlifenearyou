from zoo.shortcuts import render
from zoo.photos.models import Photo

def index(request):
    context = {
        'photos': Photo.objects.filter(
            is_visible = True
        ).select_related('created_by').order_by('-created_at')[:16]
    }
    if not request.user.is_anonymous():
        context['is_logged_in'] = True
        context['photos_of_your_favourites'] = Photo.objects.filter(
            is_visible = True
        ).filter(
            sightings__species__favourited__user = request.user
        ).select_related('created_by').order_by('-created_at')[:16]
    
    return render(request, 'explore/index.html', context)
