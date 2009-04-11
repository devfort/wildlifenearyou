from zoo.animals.models import Species
from zoo.search import lookup_species
from django.template.defaultfilters import slugify

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
            slug = slugify(details['common_name'].lower())
            while Species.objects.filter(slug = slug).count():
                slug = slug + '-'
            obj, created = Species.objects.get_or_create(
                freebase_id = details['freebase_id'],
                defaults = {
                    'slug': slug,
                    'common_name': details['common_name'],
                    'latin_name': details['scientific_name'],
                }
            )
            return obj
    else:
        return None
