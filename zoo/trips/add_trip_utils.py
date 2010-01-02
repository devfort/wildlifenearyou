import freebase
from django.utils import simplejson as json
from django.db.models import Count
from django.core.cache import cache
from zoo.animals.models import Species

FAKE_MODE = False # For developing offline

def bulk_lookup(ids, place=None):
    if not ids:
        return []
    
    cached_details = dict([
        (key.replace('freebase_species:', ''), value)
        for key, value in cache.get_many(
            'freebase_species:%s' % id for id in ids
        ).items()
    ])
    ids_to_retrieve = [id for id in ids if id not in cached_details]
    details = cached_details.values()
    
    if FAKE_MODE:
        freebase_details = FAKE_FREEBASE_BULK
    else:
        if ids_to_retrieve:
            freebase_details = freebase.mqlreadmulti(
                [_species_query(i) for i in ids_to_retrieve]
            )
        else:
            freebase_details = []
    
    for o in freebase_details:
        cache.set('freebase_species:%s' % o['id'], o)
    
    details.extend(freebase_details)
    
    detail_ids = [o['id'] for o in details]
    
    ids_to_sort_by = [id for id in ids if id in detail_ids]
    
    # Ensure details is ordered the same was is ids
    details.sort(key = lambda o: ids_to_sort_by.index(o['id']))
    
    return _annotate_database_objects(
        details,
        place = place
    )

def search(q, place=None, limit=5):
    # TODO: 1 hour cache
    if FAKE_MODE:
        fb_json = FAKE_FREEBASE_SEARCH
    else:
        fb_json = freebase.search(q,
            type = '/biology/organism_classification',
            limit = limit,
            mql_output = json.dumps([{
                'guid': None,
                'name': None,
                '/biology/organism_classification/scientific_name': None,
                '/common/topic/alias': [],
            }])
        )
        # Add an 'id' field for each result based on the 'guid' field
        fb_json = [
            dict(item.items() + [
                ('id', '/guid/%s' % item['guid'].replace('#', ''))
            ])
            for item in fb_json
        ]
    
    results = _annotate_database_objects(
        map(_tidy_up_keys, fb_json), place = place
    )
    
    # Custom ordering - things spotted here (or anywhere) take precedence
    results.sort(key = lambda o: (
        o.get('local_sightings', 0),
        o.get('total_sightings', 0),
        o.get('relevance:score', 0.0),
    ), reverse=True)
    
    return results

def _annotate_database_objects(objs, place=None):
    # Now see if any are already species in our database
    species_query = Species.objects.filter(
        freebase_id__in = [o['id'] for o in objs]
    )
    lookups = {}
    
    # Stash DB object and number of total sightings
    for s in species_query.annotate(num_sightings = Count('sightings')):
        lookups[s.freebase_id] = {
            'obj': s,
            'total_sightings': s.num_sightings,
        }
    
    if place:
        # Also stash number of local sightings
        for s in species_query.filter(
                sightings__place = place
            ).annotate(num_sightings = Count('sightings')):
            lookups[s.freebase_id]['local_sightings'] = s.num_sightings
    
    for obj in objs:
        obj['obj'] = lookups.get(obj['id'], {}).get('obj')
        obj['total_sightings'] = lookups.get(
            obj['id'], {}
        ).get('total_sightings', 0)
        obj['local_sightings'] = lookups.get(
            obj['id'], {}
        ).get('local_sightings', 0)
    
    #assert False, objs
    
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

# Useful for offline development:

FAKE_FREEBASE_SEARCH =  [{
    u'/biology/organism_classification/scientific_name': u'Ailuropoda melanoleuca',
    u'/common/topic/alias': [],
    u'guid': u'#9202a8c04000641f800000000001aa01',
    u'id': u'/en/giant_panda',
    u'name': u'Giant Panda',
    u'relevance:score': 51.357181549072266
}, {
    u'/biology/organism_classification/scientific_name': u'Ailurus fulgens',
    u'/common/topic/alias': [],
    u'guid': u'#9202a8c04000641f8000000000034937',
    u'id': u'/en/red_panda',
    u'name': u'Red Panda',
    u'relevance:score': 51.097240447998047
}, {
    u'/biology/organism_classification/scientific_name': u'Corydoras panda',
    u'/common/topic/alias': [],
    u'guid': u'#9202a8c04000641f8000000000c56b68',
    u'id': u'/en/panda_corydoras',
    u'name': u'Panda corydoras',
    u'relevance:score': 49.192520141601562
}, {
    u'/biology/organism_classification/scientific_name': None,
    u'/common/topic/alias': [],
    u'guid': u'#9202a8c04000641f80000000007682f8',
    u'id': u'/guid/9202a8c04000641f80000000007682f8',
    u'name': u'Panda',
    u'relevance:score': 39.27264404296875
}, {
    u'/biology/organism_classification/scientific_name': None,
    u'/common/topic/alias': [],
    u'guid': u'#9202a8c04000641f8000000000bd3b13',
    u'id': u'/en/dwarf_panda',
    u'name': u'Dwarf Panda',
    u'relevance:score': 32.769500732421875
}]

FAKE_FREEBASE_BULK = [{
    u'id': u'/en/giant_panda',
    u'name': u'Giant Panda',
    u'scientific_name': u'Ailuropoda melanoleuca',
    u'type': u'/biology/organism_classification'
}, {
    u'id': u'/en/red_panda',
    u'name': u'Red Panda',
    u'scientific_name': u'Ailurus fulgens',
    u'type': u'/biology/organism_classification'
}]
