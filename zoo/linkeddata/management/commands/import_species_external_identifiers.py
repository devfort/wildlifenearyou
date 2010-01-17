from django.core.management.base import BaseCommand, CommandError
from zoo.animals.models import Species

import time

class Command(BaseCommand):
    help = """
    Back-fill external ids for all species already imported from Freebase.
    """.strip()
    
    requires_model_validation = True
    can_import_settings = True
    
    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        species_with_no_external_identifiers = Species.objects.filter(
            external_identifiers__isnull = True
        )
        for species in species_with_no_external_identifiers:
            ids = species.update_external_identifiers()
            print "Done %s, got %s identifiers" % (species, len(ids))
            time.sleep(1)
