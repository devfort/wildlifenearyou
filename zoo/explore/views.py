from zoo.shortcuts import render
from zoo.photos.models import Photo

def index(request):
    return render(request, 'explore/index.html', {
        'photos': Photo.objects.filter(
            is_visible = True
        ).order_by('-created_at')[:32]
    })
