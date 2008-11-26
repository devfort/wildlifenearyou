from django.http import HttpResponse
try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET
from models import FaceAreaCategory

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

def profile_images_xml(request):
    profileImages = ET.Element('profileImages')
    for category in FaceAreaCategory.objects.all():
        faceareacategory = ET.Element('faceareacategory')
        faceareacategory.attrib = {'name': category.name}
        profileImages.append(faceareacategory)
        for area in category.areas.all():
            partlist = ET.Element('facearea')
            partlist.attrib = {
                'name': area.name,
                'description': area.description,
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
    return HttpResponse(
        '<?xml version="1.0" encoding="UTF-8"?>\n' +
        ET.tostring(profileImages), 
        content_type = 'application/xml; charset=utf8'
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
