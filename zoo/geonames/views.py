from zoo.shortcuts import render, Redirect
from utils import search_location

def set_location(request):
    response = Redirect('/')
    location = request.POST.get('location', '')
    if location:
        results = search_location(location)
        if results:
            response.set_cookie('current_location', results[0].summary())
    return response
