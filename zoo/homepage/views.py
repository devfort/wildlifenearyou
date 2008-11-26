from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseServerError
from zoo.shortcuts import render

from zoo.places.models import Place

def landing(request):
    random_zoo = Place.objects.all().order_by('?')[0]
    return render(request, 'homepage/landing.html', {
            'random_zoo': random_zoo,
    })
