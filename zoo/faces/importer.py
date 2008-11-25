import os
from django.core.files import File

IMPORT_FROM = os.path.join(os.path.dirname(__file__), 'import_these')

# ignore: hair_short*
#         accessories_barrette*
# for the moment at least

areas = ({
    # The name to use for this area
    'name': 'Hair (top)',
    # Files with this prefix go in this area
    'prefixes': [
        'hair_bangs',
        'hair_black_spikey',
        'hair_mohawk',
        'hair_short_thin',
        'hair_spikey',
    ],
    # If specified, these will be removed before auto-creating the description  
    # of the part. If not specified, the prefixes list above will be used
    'remove_prefixes': ['hair'],
}, {
    'name': 'Hair (bottom)',
    'prefixes': [
        'hair_curly',
        'hair_side',
    ],
    'remove_prefixes': ['hair'],
}, {
    'name': 'Lips',
    'prefixes': ['lips'],
}, {
    'name': 'Noses',
    'prefixes': ['nose'],
}, {
    'name': 'Hats',
    'prefixes': ['accessories_hat'],
}, {
    'name': 'Cheeks',
    'prefixes': ['cheeks'],
}, {
    'name': 'Eyelashes',
    'prefixes': ['eyelashes'],
}, {
    'name': 'Faces',
    'prefixes': ['faces'],
}, {
    'name': 'Glasses',
    'prefixes': ['glasses'],
}, {
    'name': 'Beards',
    'prefixes': ['facial_beard'],
})

from zoo.faces.models import FaceArea, FacePart

def import_faceparts(filepath = IMPORT_FROM):
    files = os.listdir(filepath)
    for area in areas:
        facearea, created = FaceArea.objects.get_or_create(
            name = area['name'],
            defaults = {'plural': area['name'] + 's', 'description': ''}
        )
        # Now find and save all the parts in that facearea
        to_add = []
        for file in files:
            for prefix in area['prefixes']:
                if file.startswith(prefix):
                    to_add.append(file)
        remove_prefixes = area.get('remove_prefixes', area['prefixes'])
        for filename in to_add:
            # Remove prefix from filename, to figure out name to use
            name_to_use = filename.split('.')[0]
            for prefix in remove_prefixes:
                if name_to_use.startswith(prefix):
                    name_to_use = name_to_use[len(prefix):]
            # Convert name_to_use to human readable
            name_to_use = name_to_use.strip('_').replace('_', ' ').title()
            # Save it to the database
            fullpath = os.path.join(filepath, filename)
            facepart = facearea.parts.create(
                description = name_to_use,
                image = '...'
            )
            facepart.image.save(filename, File(open(fullpath)))
            print "Imported %s" % facepart

