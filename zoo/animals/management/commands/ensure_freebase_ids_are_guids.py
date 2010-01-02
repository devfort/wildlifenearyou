from zoo.animals.models import Species
import freebase

def ensure_freebase_ids_are_guids():
    for species in Species.objects.exclude(freebase_id__startswith='/guid/'):
        guid = freebase.mqlread({
            'id': species.freebase_id,
            'guid': None
        })['guid']
        
        new_freebase_id = '/guid/%s' % guid[1:]
        # Does that guid already exist? If so, a merge is needed
        if Species.objects.filter(freebase_id = new_freebase_id):
            dupe = Species.objects.get(freebase_id = new_freebase_id)
            print "Duplicate: %s:%s and %s:%s - you must fix that first" % (
                species.pk, species.slug, dupe.pk, dupe.slug
            )
            continue
        
        species.freebase_id = new_freebase_id
        species.save()
        print "    %s freebase id is now %s" % (species, new_freebase_id)

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = """
    Looks for species with IDs like /en/tiger, uses the Freebase API to find 
    out their GUID and changes their freebase_id to /guid/BLAH
    """.strip()
    
    requires_model_validation = True
    can_import_settings = True
    
    def handle(self, *args, **options):
        ensure_freebase_ids_are_guids()
