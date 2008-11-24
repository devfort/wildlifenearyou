from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseServerError

from zoo.animals.models import Animal
from zoo.shortcuts import render

def animal(request, slug):
    animal = get_object_or_404(Animal, slug=slug)
    return render(request, 'animals/animal.html', {
        'animal': animal,
    })

def animals(request):
    return render(request, 'animals/animals.html', {
        'animals': Animal.objects.all(),
    })

def animal_latin(request, latin_name):
    animal = get_object_or_404(Animal, latin_name=latin_name)
    return HttpResponseRedirect(animal.urls.absolute)
