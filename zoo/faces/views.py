from django.http import HttpResponse
try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET
from models import FaceArea

"""
<profileImages>
    <facearea description="" name="Hair (top)">
        <facepart id="470" 
            src="/static/uploaded/faceparts/hair_bangs2_black.png" 
            title="Bangs2 Black"/>
    </facearea>
    ...
</profileImages>
"""

def profile_images_xml(request):
    profileImages = ET.Element('profileImages')
    for area in FaceArea.objects.all():
        partlist = ET.Element('facearea')
        partlist.attrib = {
            'name': area.name,
            'description': area.description,
        }
        profileImages.append(partlist)
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
