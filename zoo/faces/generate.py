from PIL import Image
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse
import os

SIZES = {
    'large': (None, None),
    'small': (30, 30),
    'medium': (75, 75),
}

def _key(username, size):
    return 'profile_image:/faces/%s/%s.png' % (size, username)

def generate_faces_for_user(user):
    key, keydir = user.get_profile().get_face_key_and_keydir()
    
    parts = [
        s.part 
        for s in user.selectedfaceparts.all().select_related('part')
    ]
    
    face_dir = os.path.join(settings.MEDIA_ROOT, 'faces', keydir)
    
    if not os.path.exists(face_dir):
        os.makedirs(face_dir)
    
    if os.path.exists(os.path.join(face_dir, '%s-large.png' % key)):
        return key
    
    if key == 'default':
        im = Image.open(os.path.join(
            settings.OUR_ROOT, 'static/img/default_face.png'
        ))
    else:
        im = Image.open(os.path.join(
            settings.OUR_ROOT, 'static/img/blank-face.png'
        ))
    
    for part in parts:
        im2 = Image.open(part.image.path)
        paste_transparent(im, None, im2)
    
    for size, (width, height) in SIZES.items():
        im_to_save = im.copy()
        if width and height:
            im_to_save.thumbnail((width, height), Image.ANTIALIAS)
        fp = open(os.path.join(face_dir, '%s-%s.png' % (key, size)), 'wb')
        im_to_save.save(fp, format = 'png')
        fp.close()
    
    return key

def clear_cached_images(username):
    for size in SIZES:
        key = _key(username, size)
        cache.delete(key)

def profile_image_response(request, size, username):
    key = _key(username, size)
    response = cache.get(key)
    if response:
        return response
    
    width, height = SIZES[size]
    
    im = im_for_username(username)
    if not im:
        response = HttpResponseRedirect('/static/img/default_face.png')
    else:
        if width and height:
            im.thumbnail((width, height), Image.ANTIALIAS) # modifies in place
        response = HttpResponse(content_type = 'image/png')
        im.save(response, format = 'png')
    
    cache.set(key, response)
    return response

def paste_transparent(dest, position, src):
    """
    Split RGBA src images into RGB and A to avoid
    modifying the alpha channel of the dest image.
    """
    rgba = src.split()
    mask = rgba[3]
    rgb_src = Image.merge('RGB', rgba[:3])
    dest.paste(rgb_src, position, mask)

def im_for_username(username):
    user = get_object_or_404(User, username=username)
    parts = [p.part for p in user.selectedfaceparts.all()]
    if parts:
        im = Image.open(os.path.join(
            settings.OUR_ROOT, 'static/img/blank-face.png'
        ))
        for part in parts:
            im2 = Image.open(part.image.path)
            paste_transparent(im, None, im2)
    else:
        im = Image.open(os.path.join(
            settings.OUR_ROOT, 'static/img/default_face.png'
        ))
    return im
