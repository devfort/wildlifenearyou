from django.conf import settings
from djape.client import Client, Query, FreeTextQuery
from django.db import models

class NotFound(Exception):
    pass

def doc_from_result_item(item, latlon_fields):
    """Make a document from a result item.

    """
    doc = {u'search_id': item['id']}
    for key, value in item['data'].items():
        value = value[0]
        if key in latlon_fields:
            value = map(float, value.split(' '))
        doc[key] = value
    return doc

def make_lookup(dbname, latlon_fields=[]):
    client = Client(settings.XAPIAN_BASE_URL, dbname)
    def lookup(id):
        result = client.get(id)
        if len(result['items']) == 1:
            item = result['items'][0]
            return doc_from_result_item(item, latlon_fields)
        else:
            raise NotFound, id
    return lookup

def make_searcher(dbname, latlon_fields=[]):
    client = Client(settings.XAPIAN_BASE_URL, dbname)
    def search(q, num=0):
        results = client.search(Query(q), end_rank=num)
        for item in results['items']:
            yield doc_from_result_item(item, latlon_fields)
    return search

def make_db_searcher(dbname, db_prefix=None, latlon_fields=[]):
    # A DB searcher knows that the results will be just search_ids, but each
    # one will be something like "places.Place:34" - it looks up the model
    # and uses .in_bulk(ids) to load those ORM objects, then returns them.
    client = Client(settings.XAPIAN_BASE_URL, dbname, db_prefix)
    def search(q, num=0, details=False, latlon=False, default_op=Query.OP_AND):
        # If details=True, it returns a tuple pair - the first item is the 
        # results list it would normally return, the second is the full Xapian
        # results object.
        q = FreeTextQuery(q, default_op=default_op)
        query = Query()
        query.part = q
        if latlon and latlon_fields:
            if not isinstance(latlon, basestring): # deal with (lat, lon) 
                latlon = ' '.join(latlon)
            query.sort_by_distance(latlon_fields[0], latlon)
        results = client.search(query, end_rank=num)
        search_ids = [
            item['id'] for item in results['items']
        ]
        to_grab = {}
        for search_id in search_ids:
            model_key, id = search_id.split(':')
            to_grab.setdefault(model_key, []).append(id)
        grabbed = {}
        # Now do an in_bulk query for each of the model_keys in to_grab
        for model_key, ids in to_grab.items():
            klass = models.get_model(*model_key.split('.'))
            for id, obj in klass.objects.in_bulk(ids).items():
                grabbed['%s:%s' % (model_key, id)] = obj
        # Finally, return objects for the search_ids in the correct order
        objects = [grabbed[search_id] for search_id in search_ids]
        if results.get('spell_corrected', False):
            spell_corrected = results['spellcorr_q']
        else:
            spell_corrected = None
        if not details:
            return objects
        else:
            return objects, results, spell_corrected
    
    return search

def make_db_deleter(dbname, prefix=None):
    client = Client(settings.XAPIAN_BASE_URL, dbname, prefix)
    def delete_database():
        client.deldb()
    return delete_database

search_locations = make_searcher(
    settings.XAPIAN_LOCATION_DB, latlon_fields = ['latlon']
)
lookup_location = make_lookup(
    settings.XAPIAN_LOCATION_DB, latlon_fields = ['latlon']
)
search_species = make_searcher(settings.XAPIAN_SPECIES_DB)
lookup_species = make_lookup(settings.XAPIAN_SPECIES_DB)

search_places = make_db_searcher(
    'placeinfo', settings.XAPIAN_PERSONAL_PREFIX,
    latlon_fields = ['latlon']
)
delete_places = make_db_deleter(
    'placeinfo', settings.XAPIAN_PERSONAL_PREFIX,
)

# Known species index holds only species which we have some information about,
# unlike the regular species index which has 44,000 animals including many 
# thot our site doesn't care about at all.
search_known_species = make_db_searcher(
    'known_species', settings.XAPIAN_PERSONAL_PREFIX
)
delete_known_species = make_db_deleter(
    'known_species', settings.XAPIAN_PERSONAL_PREFIX
)


