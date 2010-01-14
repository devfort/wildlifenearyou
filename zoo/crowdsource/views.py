from photos.models import Photo
from zoo.shortcuts import render
from photos.views import filter_visible_photos
from django.db.models import Count

def index(request):
    return render(request, 'crowdsource/index.html')

def identify_species(request):
    photos = Photo.objects.exclude(
        has_no_species = True
    ).exclude(
        trip__isnull = True
    ).filter(
        sightings__isnull = True,
        is_visible = True,
    ).select_related('created_by').order_by('-created_at')
    
    return render(request, 'crowdsource/identify_species.html', {
        'photos': photos,
        'page': request.GET.get('page', '1') # used by caching template tag
    })
