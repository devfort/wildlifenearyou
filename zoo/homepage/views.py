from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseServerError
from zoo.shortcuts import render

def landing(request):
    return render(request, 'homepage/landing.html', {
    })
    
