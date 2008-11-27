from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseServerError
from zoo.shortcuts import render

from zoo.places.models import Place

def landing(request):
    if Place.objects.all():
        random_zoo = Place.objects.all().order_by('?')[0]
    else:
        random_zoo = None
        
    return render(request, 'homepage/landing.html', {
        'random_zoo': random_zoo,
    })
