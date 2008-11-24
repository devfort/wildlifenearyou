from django.http import HttpResponse
from xml.etree import ElementTree as ET
from models import FaceArea

def profile_images_xml(request):
    profileImages = ET.Element('profileImages')
    for area in FaceArea.objects.all():
        partlist = ET.Element(area.plural.lower().replace(' ', '-'))
        partlist.attrib = {
            'name': area.name,
            'plural': area.plural,
            'description': area.description,
        }
        profileImages.append(partlist)
        for part in area.parts.all():
            p = ET.Element(area.name.lower().replace(' ', '-'))
            p.attrib = {
                'src': part.image.url,
                'id': str(part.id),
                'title': part.description,
            }
            partlist.append(p)
    return HttpResponse(
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