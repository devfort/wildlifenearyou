from django.contrib.auth.decorators import login_required
from django import forms
from django.http import HttpResponseRedirect as Redirect
from zoo.shortcuts import render
from models import Photo

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
