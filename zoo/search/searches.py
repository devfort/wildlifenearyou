from django.conf import settings
from djape.client import Client, Query

def search_species(q, num=0):
    client = Client(settings.XAPIAN_BASE_URL, settings.XAPIAN_SPECIES_DB)
    results = client.search(Query(q), end_rank=num)
    for item in results['items']:
        yield {
            u'search_id': item['id'],
            u'common_name': item['data']['common_name'][0],
            u'scientific_name': item['data']['scientific_name'][0],
        }

def make_searcher(dbname, latlon_fields=[]):
    client = Client(settings.XAPIAN_BASE_URL, dbname)
    def search(q, num=0):
        results = client.search(Query(q), end_rank=num)
        for item in results['items']:
            doc = {u'search_id': item['id']}
            for key, value in item['data'].items():
                value = value[0]
                if key in latlon_fields:
                    value = map(float, value.split(' '))
                doc[key] = value
            yield doc
    return search

search_locations = make_searcher(
    settings.XAPIAN_LOCATION_DB, latlon_fields = ['latlon']
)
