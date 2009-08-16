import freebase
from django.utils import simplejson as json
from zoo.animals.models import Species

def bulk_lookup(ids):
    if not ids:
        return []
    return _annotate_database_objects(
        freebase.mqlreadmulti([_species_query(i) for i in ids])
    )

def search(q, limit=5):
    return _annotate_database_objects(map(_tidy_up_keys, freebase.search(q,
        type = '/biology/organism_classification',
        limit = limit,
        mql_output = json.dumps([{
            'id': None,
            'name': None,
            '/biology/organism_classification/scientific_name': None,
            '/common/topic/alias': [],
        }])
    )))

def _annotate_database_objects(objs):
    # Now see if any are already species in our database
    species = Species.objects.filter(
        freebase_id__in = [o['id'] for o in objs]
    )
    lookups = {}
    for s in species:
        lookups[s.freebase_id] = s
    for obj in objs:
        obj['obj'] = lookups.get(obj['id'], None)
    return objs

def _species_query(id):
    return {
        'id': id,
        'type': '/biology/organism_classification',
        'name': None,
        'scientific_name': None,
    }

def _tidy_up_keys(d):
    return dict([
        (key.split('/')[-1], value) for key, value in d.items()
    ])
