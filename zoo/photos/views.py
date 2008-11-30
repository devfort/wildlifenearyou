from django import forms
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden

from models import Photo
from zoo.shortcuts import render
from zoo.trips.models import Trip
from zoo.places.models import Place
from zoo.animals.forms import SpeciesField

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
                '/profile/%s/' % request.user.username
            ))
    else:
        form = UploadPhotoForm()

    return render(request, 'photos/upload.html', {
        'form': form,
        'attach_to': place,
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
            # If user has account 7 days or older, or is staff
            # go live straight away
            if request.user.get_profile().is_not_brand_new_account() or \
                request.user.is_staff:
                photo.is_visible = True
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
    })

class PhotoOnlyForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ('photo')

@login_required
def edit_photo(request, username, photo_id):
    if username != request.user.username:
        raise HttpResponseForbidden
    photo = get_object_or_404(Photo, id=photo_id, created_by=request.user)
    if request.method == 'POST':
        form = PhotoEditForm(request.POST)
        if form.is_valid():
            photo.title = form.cleaned_data['title']
            photo.save()
            return HttpResponseRedirect(photo.get_absolute_url())
    else:
        form = PhotoEditForm()
    return render(request, 'photos/edit.html', {
        'form': form,
        'photo': photo,
    })

@login_required
def set_species(request, username, photo_id):
    from zoo.trips.models import Sighting
    if username != request.user.username:
        raise HttpResponseForbidden
    # Should be POSTed to with a list of 'saw' values
    photo = get_object_or_404(Photo, id=photo_id, created_by=request.user)
    assert photo.trip, \
        "A photo should have a trip if you're trying to add sightings to it"
    # The sightings should already exist on that trip, just hook up the photo
    for id in request.POST.getlist('saw'):
        #print "Processing species ID %s" % id
        # Silently discard IDs that do not correspond with sightings
        try:
            sighting = photo.trip.sightings.get(species__id = id)
            #print "  Found sighting %s" % sighting
        except Sighting.DoesNotExist:
            #print "  Could not find matching sighting"
            continue
        assert request.user == sighting.created_by
        photo.sightings.add(sighting)
    return HttpResponseRedirect(photo.get_absolute_url())

class PhotoEditForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ('title')

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
