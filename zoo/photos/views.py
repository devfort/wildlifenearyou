from django import forms
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import Q

from models import Photo
from zoo.shortcuts import render
from zoo.trips.models import Trip, Sighting
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
        form = PhotoEditForm(request.user, request.POST)
        if form.is_valid():
            trip_has_changed = (photo.trip != form.cleaned_data['trip'])
            old_trip = photo.trip
            
            photo.title = form.cleaned_data['title']
            
            if trip_has_changed:
                photo.trip = form.cleaned_data['trip']
            
            photo.save()
            
            # If the user changed the trip AND that photo has sightings 
            # associated with it, we need to create new sightings for those 
            # animals attached to the new trip and re-target the photo 
            # relationships to point at those new sightings instead. We'll 
            # leave the old sightings where they are - the user can delete 
            # them later if they want to.
            if trip_has_changed:
                sightings = list(photo.sightings.all())
                # Clear out those relationships (does not delete sightings)
                photo.sightings.clear()
                for sighting in sightings:
                    # Ensure a sighting for that species exists for new trip
                    kwargs = {'trip': photo.trip}
                    if sighting.species:
                        kwargs['species'] = sighting.species
                    else:
                        kwargs['species_inexact'] = sighting.species_inexact
                    matching_sightings = Sighting.objects.filter(**kwargs)
                    if matching_sightings:
                        # Attach the photo to the first of those matches
                        photo.sightings.add(matching_sightings[0])
                    else:
                        # Create a new sighting for that species on that place
                        del kwargs['trip'] # re-using kwargs from earlier
                        kwargs['place'] = trip.place
                        photo.sightings.create(**kwargs)
            
            return HttpResponseRedirect(photo.get_absolute_url())
    else:
        form = PhotoEditForm(request.user, instance=photo)
    return render(request, 'photos/edit.html', {
        'form': form,
        'photo': photo,
    })

@login_required
def delete_photo(request, username, photo_id):
    user = get_object_or_404(User, username=username)
    photo = get_object_or_404(Photo, id=photo_id, created_by=user)
    assert request.user.id == user.id, "You can only delete your own trips!"
    if request.POST.get('confirm_delete'):
        # Delete the photo
        trip = photo.trip
        photo.delete()
        if trip:
            trip.save() # Re-index to update denormalised stuff
        
        return HttpResponseRedirect(
            reverse('accounts-profile', args=(username,))
        )
    
    return render(request, 'photos/delete.html', {
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
            sighting = photo.trip.sightings.filter(pk = id)[0]
            #print "  Found sighting %s" % sighting
        except IndexError:
            #print "  Could not find matching sighting"
            continue
        assert request.user == sighting.created_by
        photo.sightings.add(sighting)
    return HttpResponseRedirect(photo.get_absolute_url())

class PhotoEditForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(PhotoEditForm, self).__init__(*args, **kwargs)
        self.fields['trip'].queryset = Trip.objects.filter(created_by=user)

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

def user_photos(request, username):
    user = get_object_or_404(User, username = username)
    return render(request, 'photos/user_photos.html', {
        'profile': user.get_profile(),
        'photos': filter_visible_photos(user.photos, request.user),
    })

def user_photos_by_trip(request, username):
    user = get_object_or_404(User, username = username)
    trips = []
    photos_to_display_per_trip = 5
    for trip in Trip.objects.filter(
            created_by = user, photos__isnull = False
        ).distinct().order_by('-start'):
        photos = filter_visible_photos(
            trip.photos, request.user
        )
        photo_count = photos.count()
        trips.append({
            'trip': trip,
            'visible_photos': photos[:photos_to_display_per_trip],
            'more_photos': max(photo_count - photos_to_display_per_trip, 0),
        })
    
    return render(request, 'photos/user_photos_by_trip.html', {
        'profile': user.get_profile(),
        'trips': trips,
    })

def user_photos_unassigned(request, username):
    user = get_object_or_404(User, username = username)
    if request.user == user:
        return user_photos_bulk_assign(request, user)
    
    return render(request, 'photos/user_photos_unassigned.html', {
        'profile': user.get_profile(),
        'photos': filter_visible_photos(
            photos = Photo.objects.filter(
                created_by = user, trip__isnull=True
            ).order_by('created_at').distinct(),
            user = request.user
        )
    })

@login_required
def user_photos_bulk_assign(request, user):
    assert user == request.user
    photos = Photo.objects.filter(
        created_by = user, trip__isnull=True
    ).order_by('created_at').distinct()
    
    they_forgot_to_select_some_photos = False
    they_forgot_to_select_a_trip = False
    
    if request.method == 'POST':
        photo_ids = request.POST.getlist('selected_photos')
        trip_id = request.POST.get('trip')
        if not photo_ids or not trip_id:
            if not photo_ids:
                they_forgot_to_select_some_photos = True
            elif not trip_id:
                they_forgot_to_select_a_trip = True
        else:
            
            photos = Photo.objects.filter(id__in = photo_ids).filter(
                created_by = request.user
            )
            trip = get_object_or_404(Trip, pk=trip_id, created_by=request.user)
            # Assign the photos to that trip
            for p in photos:
                p.trip = trip
                p.save()
            # Force a re-index of trip
            trip.save()
            # Redirect to that trip's page (TODO: trip's photo page instead)
            return HttpResponseRedirect(trip.get_absolute_url())
    
    return render(request, 'photos/user_photos_bulk_assign.html', {
        'profile': user.get_profile(),
        'photos': photos,
        'trip_count': Trip.objects.filter(created_by=user).count(),
        'they_forgot_to_select_some_photos': they_forgot_to_select_some_photos,
        'they_forgot_to_select_a_trip': they_forgot_to_select_a_trip,
        'form': TripSelectForm(user)
    })

class TripSelectForm(forms.Form):
    trip = forms.ModelChoiceField(Trip)
    def __init__(self, user, *args, **kwargs):
        super(TripSelectForm, self).__init__(*args, **kwargs)
        self.fields['trip'].queryset = Trip.objects.filter(created_by=user)

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
        photos = Photo.objects.filter(
            is_visible=False).filter(moderated_by=None
        )
        return render(request, 'photos/moderate.html', {
            'photos': photos[:10],
            'total': photos.count()
        })

def filter_visible_photos(photos, user):
    "photos is a QuerySet of photos, user is the user who wants to view them"
    return photos.filter(
        Q(is_visible = True) | Q(created_by = user)
    ).distinct()

