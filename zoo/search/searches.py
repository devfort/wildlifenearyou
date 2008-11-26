from django.conf import settings
from djxappy_client import XappyClient, Query
client = XappyClient(settings.XAPIAN_BASE_URL, settings.XAPIAN_SPECIES_DB)

def search_species(q, num=0):
    results = client.search(Query(q), end_rank=num)
    for item in results['items']:
        yield {
            'search_id': item['id'],
            'common_name': item['data']['common_name'],
            'scientific_name': item['data']['scientific_name'],
        }
