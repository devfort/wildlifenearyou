from django import forms
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect as Redirect
from django.contrib.auth.decorators import login_required

from models import Photo
from zoo.shortcuts import render
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
            return Redirect(redirect_to or (
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

from django import forms
class PhotoSpeciesForm(forms.Form):
    species1 = SpeciesField(required = False)
    species2 = SpeciesField(required = False)
    species3 = SpeciesField(required = False)
    species4 = SpeciesField(required = False)

def photo(request, username, photo_id):
    photo = get_object_or_404(
        Photo, created_by__username=username, pk=photo_id
    )

    if request.method == 'POST':
        form = PhotoSpeciesForm(request.POST)
        if form.is_valid():
            print "OK", form.cleaned_data
            print "ERR", form.errors
    else:
        form = PhotoSpeciesForm()

    return render(request, 'photos/photo.html', {
        'photo': photo,
        'form': form,
    })

def all(request):
    return render(request, 'photos/all.html', {
        'photos': Photo.objects.all().order_by('-created_at'),
    })
