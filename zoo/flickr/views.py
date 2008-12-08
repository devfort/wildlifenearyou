from django import forms
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden

from zoo.shortcuts import render
from zoo.photos.models import Photo
from zoo.trips.models import Trip
from client import Flickr

@login_required
def import_trip(request, username, trip_id):
    user = get_object_or_404(User, username=username)
    trip = get_object_or_404(Trip, id=trip_id, created_by=user)
    assert username == request.user.username
    
    # Does the user have a Flickr auth cookie? We use a cookie because Flickr
    # say "Authentication cookies should only be stored for a single session"
    # on this page: http://www.flickr.com/services/api/auth.spec.html
    flickr_token = request.COOKIES.get('flickr_token')
    if flickr_token:
        # Show the user their sets so they can pick one
        sets = Flickr(
            token = flickr_token
        ).photosets_getList()['photosets']['photoset']
        return render(request, 'flickr/pick_a_set.html', {
            'trip': trip,
            'sets': sets,
        })
    else:
        # We're about to send them off to Flickr to authenticate, but first 
        # we need to set a cookie specifying where they should come BACK to 
        # since Flickr will return them to /flickr-callback/
        response = HttpResponseRedirect(Flickr().web_login_url("write"))
        response.set_cookie('flickr_return_to', request.path)
        return response

def flickr_error(request, msg):
    return render(request, 'flickr/error.html', {
        'msg': msg,
    })

@login_required
def import_trip_from_set(request, username, trip_id, set_id):
    "Allows the user to pick photos from a Flickr set that they wish to import"
    user = get_object_or_404(User, username=username)
    trip = get_object_or_404(Trip, id=trip_id, created_by=user)
    assert username == request.user.username
    
    # Load the photos from the set
    flickr_token = request.COOKIES.get('flickr_token')
    if not flickr_token:
        return flickr_error(request, 'Your Flickr token is missing')
    
    flickr = Flickr(token = flickr_token)
    set_info = flickr.photosets_getInfo(set_id)
    photos = flickr.photosets_getPhotos(set_id)
    
    if request.method == 'POST':
        # Actually do the import
        assert False, request.POST
    
    return render(request, 'flickr/pick_photos_from_set.html', {
        'photos': photos,
        'set': set_info,
    })
    
    
    
    
    

def flickr_callback(request):
    return_to = request.COOKIES.get('flickr_return_to', '/')
    flickr_token = Flickr().get_token(request.GET.get('frob', ''))
    response = HttpResponseRedirect(return_to)
    response.set_cookie('flickr_token', flickr_token)
    response.set_cookie('flickr_return_to', '')
    return response
