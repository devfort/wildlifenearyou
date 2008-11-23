from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseServerError

from zoo.animals.models import Animal

def animal(request, common_name):
    animal = get_object_or_404(Animal, common_name=common_name)    
    return HttpResponse('hello there, %s' % (animal,))

def animal_latin(request, latin_name):
    animal = get_object_or_404(Animal, latin_name=latin_name)
    return HttpResponseRedirect(animal.urls.absolute)
