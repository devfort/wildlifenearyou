from django.contrib.auth.decorators import login_required
from django import forms
from django.http import HttpResponseRedirect as Redirect
from zoo.shortcuts import render
from django.shortcuts import get_object_or_404
from models import Photo
from zoo.places.models import Place

@login_required
def upload(request):
    if request.method == 'POST':
        # Process uploaded photo
        form = UploadPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return Redirect('/profile/%s/' % request.user.username)
    else:
        form = UploadPhotoForm()
    
    return render(request, 'photos/upload.html', {
        'form': form,
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
    if request.method == 'POST':
        # Process uploaded photo
        form = UploadPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit = False)
            obj.place = place
            obj.save()
            return Redirect(place.get_absolute_url())
    else:
        form = UploadPhotoForm()
    
    return render(request, 'photos/upload.html', {
        'form': form,
        'attach_to': place,
    })

def photo(request, username, photo_id):
    photo = get_object_or_404(
        Photo, created_by__username = username, pk = photo_id
    )
    return render(request, 'photos/photo.html', {
        'photo': photo,
    })
