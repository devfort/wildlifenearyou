from django.http import HttpResponse
try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET
from models import FaceAreaCategory, FaceArea
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from PIL import Image
from django.contrib.auth.decorators import login_required
from zoo.shortcuts import render

"""
<profileImages>
    <faceareacategory name="Hair">
        <facearea description="" name="Hair (top)">
            <facepart id="470" 
                src="/static/uploaded/faceparts/hair_bangs2_black.png" 
                title="Bangs2 Black"/>
        </facearea>
        ...
    </faceareacategory>
</profileImages>
"""

@login_required
def profile_images_xml(request):
    profileImages = ET.Element('profileImages')
    for category in FaceAreaCategory.objects.for_user(request.user):
        faceareacategory = ET.Element('faceareacategory')
        faceareacategory.attrib = {'name': category.name}
        profileImages.append(faceareacategory)
        for area in category.areas.all():
            partlist = ET.Element('facearea')
            partlist.attrib = {
                'name': area.name,
                'description': area.description,
                'id': str(area.id),
                'small': area.is_small and '1' or '0',
            }
            faceareacategory.append(partlist)
            for part in area.parts.all():
                p = ET.Element('facepart')
                p.attrib = {
                    'src': part.image.url,
                    'id': str(part.id),
                    'title': part.description,
                }
                partlist.append(p)
    return XmlResponse(ET.tostring(profileImages))

@login_required
def profile_xml(request):
    return profile_image_xml(request, request.user.username)

def profile_image_xml(request, username):
    user = get_object_or_404(User, username=username)
    parts = [p.part for p in user.selectedfaceparts.all()]
    profile = ET.Element('profile')
    profile.attrib = {
        'user_id': str(user.id),
        'username': username,
        'name': user.get_full_name(),
        'update-url': '/faces/update/',
    }
    for part in parts:
        facepart = ET.Element('facepart')
        profile.append(facepart)
        facepart.attrib = {
            'area': part.area.name,
            'area_id': str(part.area.id),
            'src': part.image.url,
            'part_id': str(part.id),
            'title': part.description,
        }
    return XmlResponse(ET.tostring(profile))

from django.conf import settings
import os

def paste_transparent(dest, position, src):
    """
    Split RGBA src images into RGB and A to avoid
    modifying the alpha channel of the dest image.
    """
    rgba = src.split()
    mask = rgba[3]
    rgb_src = Image.merge('RGB', rgba[:3])
    dest.paste(rgb_src, position, mask)

def profile_image(request, username, just_the_image_please=False):
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
    
    if just_the_image_please:
        return im
    
    response = HttpResponse(content_type = 'image/png')
    im.save(response, format = 'png')
    return response

def profile_image_resized(request, username, width=30, height=30):
    im = profile_image(request, username, just_the_image_please=True)
    if not im:
        return HttpResponseRedirect('/static/img/default_face.png')
    im.thumbnail((width, height), Image.ANTIALIAS) # modifies in place
    response = HttpResponse(content_type = 'image/png')
    im.save(response, format = 'png')
    return response

class XmlResponse(HttpResponse):
    def __init__(self, xml):
        super(XmlResponse, self).__init__(
            '<?xml version="1.0" encoding="UTF-8"?>\n' + xml,
            content_type = 'application/xml; charset=utf8'
        )

@login_required
def update(request):
    flash = request.POST.get('flash')
    # This is mostly for the flash player to talk to, but a rudimentary 
    # interface is provided for the impatient
    msg = ''
    user = request.user
    if request.method == 'POST':
        post = dict([
            (key, value) for key, value in request.POST.items()
            if value != '0'
        ])
        form = FaceUpdateForm(user, post)
        if form.is_valid():
            # Over-write the user's profile data
            user.selectedfaceparts.all().delete()
            for key, part in form.cleaned_data.items():
                if not part:
                    continue # Skip the ones that they didn't fill in
                area_id = int(key.split('_')[1])
                user.selectedfaceparts.create(
                    part = part,
                    user = user,
                    area = FaceArea.objects.get(pk = area_id),
                )
            msg = 'Updated!'
            if flash:
                return XmlResponse('<result status="ok" />')
        else:
            if flash:
                return XmlResponse('<result status="errors" />')
    else: # GET requests should always be from HTML, not flash
        form = FaceUpdateForm(user)
    
    # TODO: If it's the flash player serve back XML instead
    return render(request, 'faces/update.html', {
        'form': form,
        'msg': msg,
    })

from django import forms
class FaceUpdateForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        # Dynamically add a choicefield for each facearea that the user has 
        # access to
        super(FaceUpdateForm, self).__init__(*args, **kwargs)
        for area in FaceArea.objects.for_user(user):
            self.fields['area_%s' % area.id] = forms.ModelChoiceField(
                area.parts.all(),
                label = area.name,
                required = False,
            )
        if not args:
            # First time we've displayed; set initial to user's current face
            self.initial = dict(
                ['area_%s' % selected.area.id, str(selected.part.id)]
                for selected in user.selectedfaceparts.all()
            )

"""
<?xml version="1.0" encoding="utf-8"?>
<profileImages>
	<faces>
		<face src="face1.png" id="uid" title="pale skin" />	
	</faces>
	<eyes>
		<eye src="eye1.png" id="uid" title="blue eyes" />
	</eyes>
	<noses>
		<nose src="nose1.png" id="uid" title="nose 1" />
	</noses>
	<ears>
		<ear src="ear1.png" id="uid" title="ear 1" />
	</ears>
	<mouths>
		<mouth src="mouth1.png" id="uid" title="mouth 1" />
	</mouths>
	<cheeks>
		<cheek src="cheeck1.png" id="uid" title="cheek 1" />
	</cheeks>
	<facialHairs>
		<facialHair src="facialHair1.png" id="uid" title="facial Hair  1" />
	</facialHairs>
	<hairs>
		<hair src="hair1.png" id="uid" title="Hair  1" />
	</hairs>
	<hairAccessories>
		<hairAccessorie src="hairaccessory1.png" id="uid" title="Hair Accessorie 1" />
	</hairAccessories>
</profileImages>
"""
