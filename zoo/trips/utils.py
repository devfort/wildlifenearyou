from zoo.animals.models import Species
from zoo.search import lookup_species

def lookup_xapian_or_django_id(id):
    if id.startswith('s_'):
        id = id[2:]
        try:
            return Species.objects.get(pk = id)
        except Species.DoesNotExist:
            return None
    elif id.startswith('x_'):
        id = id[2:]
        # Look it up in Xapian
        try:
            details = lookup_species(id)
        except NotFound:
            return None
        # If it's a Django object already, return that
        try:
            return Species.objects.get(freebase_id = details['freebase_id'])
        except Species.DoesNotExist:
            # Save it to the database
            obj, created = Species.objects.get_or_create(
                slug = details['common_name'].replace(' ', '-').lower(),
                common_name = details['common_name'],
                latin_name = details['scientific_name'],
                freebase_id = details['freebase_id'],
            )
            return obj
    else:
        return None
