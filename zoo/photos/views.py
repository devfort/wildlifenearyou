from django import forms
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.conf import settings

from models import Photo
from zoo.shortcuts import render
from zoo.trips.models import Trip
from zoo.places.models import Place
from zoo.animals.forms import SpeciesField

import datetime

@login_required
def upload(request, place=None, redirect_to=None):
    if request.method == 'POST':
        # Process uploaded photo
        form = UploadPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit = False)
            if place:
                obj.place = place
            # If user has account 7 days or older, or is staff
            # go live straight away
            if request.user.get_profile().is_not_brand_new_account() or \
                request.user.is_staff:
                obj.is_visible = True
            obj.save()
            return HttpResponseRedirect(redirect_to or (
                reverse('accounts-profile', args=(request.user,))
            ))
    else:
        form = UploadPhotoForm()

    return render(request, 'photos/upload.html', {
        'form': form,
        'attach_to': place,
        'limit': settings.FILE_UPLOAD_SIZE_LIMIT,
    })

class UploadPhotoForm(forms.ModelForm):
    class Meta:
        fields = ('title', 'photo')
        model = Photo

@login_required
def upload_place(request, country_code, slug):
    place = get_object_or_404(Place,
        slug=slug,
        country__country_code=country_code
    )
    return upload(request, place, redirect_to = place.get_absolute_url())

@login_required
def upload_trip(request, username, trip_id):
    user = get_object_or_404(User, username=username)
    trip = get_object_or_404(Trip, id=trip_id, created_by=user)
    # The user should have got here via a file upload PUSH. If so, we 
    # create the photo straight away and redirect them straight to the edit
    # page.
    if request.method == 'POST':
        form = PhotoOnlyForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit = False)
            photo.trip = trip
            # Set the title to the filename, if provided
            photo.title = form.cleaned_data['photo'].name
            # If user has account 7 days or older, or is staff
            # go live straight away
            if request.user.get_profile().is_not_brand_new_account() or \
                request.user.is_staff:
                photo.is_visible = True
            photo.save()
            # Redirect them straight to the edit page for that photo
            return HttpResponseRedirect(photo.get_absolute_url() + 'edit/')

    form = PhotoOnlyForm()
    return render(request, 'photos/single_upload.html', {
        'form': form,
        'action': request.path,
        'limit': settings.FILE_UPLOAD_SIZE_LIMIT,
    })

class PhotoOnlyForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ('photo')

@login_required
def edit_photo(request, username, photo_id):
    """
    We force people to assign a photo to a place before they can add any 
    animals. This is so animals in the photo can be represented using 
    sightings attached to that trip. That way we can offer people the list of
    species from the trip for that photo, and if they add a different 
    """
    if username != request.user.username:
        return HttpResponseForbidden('Not your photo')
    photo = get_object_or_404(Photo, id=photo_id, created_by=request.user)
    if request.method == 'POST':
        form = PhotoEditForm(request.POST)
        if form.is_valid():
            photo.title = form.cleaned_data['title']
            photo.trip = form.cleaned_data['trip']
            photo.save()
            return HttpResponseRedirect(photo.get_absolute_url())
    else:
        form = PhotoEditForm(instance=photo)
    return render(request, 'photos/edit.html', {
        'form': form,
        'photo': photo,
    })

@login_required
def set_species(request, username, photo_id):
    from zoo.trips.models import Sighting
    if username != request.user.username:
        return HttpResponseForbidden()
    # Should be POSTed to with a list of 'saw' values
    photo = get_object_or_404(Photo, id=photo_id, created_by=request.user)
    assert photo.trip, \
        "A photo should have a trip if you're trying to add sightings to it"
    # The sightings should already exist on that trip, just hook up the photo
    for id in request.POST.getlist('saw'):
        #print "Processing species ID %s" % id
        # Silently discard IDs that do not correspond with sightings
        try:
            sighting = photo.trip.sightings.filter(species__id = id)[0]
            #print "  Found sighting %s" % sighting
        except IndexError:
            #print "  Could not find matching sighting"
            continue
        assert request.user == sighting.created_by
        photo.sightings.add(sighting)
    return HttpResponseRedirect(photo.get_absolute_url())

class PhotoEditForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ('title', 'trip')

def photo(request, username, photo_id):
    photo = get_object_or_404(
        Photo, created_by__username=username, pk=photo_id
    )
    return render(request, 'photos/photo.html', {
        'photo': photo,
    })

def all(request):
    return render(request, 'photos/all.html', {
        'photos': Photo.objects.all().order_by('-created_at'),
    })

@login_required
def moderate(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()
        
    if request.method == 'POST':
        for k in request.POST.keys():            
            if k[:6]=='photo-':
                v = request.POST[k]
                if v=='0':
                    continue
                ppk = int(k[6:])
                photo = Photo.objects.get(pk=ppk)
                photo.moderated_by = request.user
                photo.moderated_at = datetime.datetime.now()
                if v=='2':
                    photo.is_visible = True
                photo.save()
        return HttpResponseRedirect(reverse('moderate-photos'))
    else:
        photos = Photo.objects.filter(is_visible=False).filter(moderated_by=None)
        return render(request, 'photos/moderate.html', { 'photos': photos[:10], 'total': photos.count() })
