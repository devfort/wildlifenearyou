from zoo.xapian_client import search
from models import Geoname

def search_location(q):
    result = search(q)
    ids = [i['data']['text'][0].split(',')[-1] for i in result['items']]
    objects = Geoname.objects.in_bulk(ids)
    return [objects[int(id.strip())] for id in ids]
