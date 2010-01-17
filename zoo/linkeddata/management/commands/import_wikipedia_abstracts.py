from django.core.management.base import BaseCommand, CommandError
from zoo.animals.models import Species
from zoo.linkeddata.models import WikipediaAbstract, \
    wikipedia_abstract_from_dbpedia
import time

class Command(BaseCommand):
    help = """
    Import Wikipedia abstracts for species, using dbpedia and SPARQL
    """.strip()
    
    requires_model_validation = True
    can_import_settings = True
    
    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        no_abstract = Species.objects.filter(
            wikipedia_abstracts__isnull = True
        )
        
        for species in no_abstract:
            dbpedia_keys = species.external_identifiers.filter(
                source = 'sameAs',
                namespace = 'http://dbpedia.org'
            ).values_list("key", flat=True)
            for key in dbpedia_keys:
                k = key.split('/')[-1]
                abstract = wikipedia_abstract_from_dbpedia(k)
                time.sleep(2)
                if abstract is not None:
                    species.wikipedia_abstracts.create(
                        abstract = abstract
                    )
                    break
            
            print "Done %s" % species
