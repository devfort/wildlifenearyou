import os
from djape.client import Client, Document
from django.conf import settings

FILEPATH = os.path.join(os.path.dirname(__file__), 'data/GB.txt')

def import_from_file(filepath = FILEPATH):
    import os
    lines = open(
        os.path.join(os.path.dirname(__file__), 'data/GB.txt')
    ).readlines()
    fields = (
        'country_code', 'postal_code', 'place_name', 'admin_name1',
        'admin_code1', 'admin_name2', 'admin_code2', 'admin_name3',
        'latitude', 'longitude', 'accuracy'
    )
    # NOTHING uses admin_name1 or admin_name3 (in GB.txt)
    # admin_name2 appears to be the county
    # place_name is the town (probably)
    # postal_code is first three letters of postal code
    for line in lines:
        line = line.strip('\n')
        if not line:
            continue
        yield dict(zip(fields, line.split("\t")))

def import_into_xapian():
    client = Client(
        settings.XAPIAN_BASE_URL, settings.XAPIAN_LOCATION_DB
    )
    try:
        client.deldb()
    except: # BAD: Naked except
        pass
    client.newdb([{
        'field_name': 'place_name',
        'store': True,
        'freetext': {'language': 'en'} # language used for stemming
    }, {
        'field_name': 'county', # Maps to admin_name2
        'store': True,
        'freetext': {}
    }, {
        'field_name': 'country_code',
        'store': True,
        'freetext': {} # TODO: Use exact match here, not yet implemented
    }, {
        'field_name': 'postal_code',
        'store': True,
        'freetext': {} # TODO: Can we do prefix search only?
    }, {
        'field_name': 'description',
        'store': True, # stored but not indexed
    }, {
        'field_name': 'latlon',
        'store': True,
        'type': 'geo',
        'geo': {}, # no options yet
    }])
    # We have a database!
    
    # We throw away anything that results in a description that we have 
    # already used for something else. There are only 213 (out of 27,000)
    # where a duplicate description has more than one lat/lon pair - so 
    # we've chosen to just discard those.
    seen_descriptions = set()
    
    # Now we create documents
    queue = []
    count = 0
    for row in import_from_file():
        # Some (3) of them don't have lat or lon - ignore those
        if not (row['latitude'] and row['longitude']):
            continue
        description = make_description(row)
        if description in seen_descriptions:
            continue
        seen_descriptions.add(description)
        count += 1
        doc = Document()
        # doc.id = 'X' will over-ride auto ID /AND/ cause replace if exists
        doc.extend([
            ('place_name', row['place_name']),
            ('county', row['admin_name2']),
            ('postal_code', row['postal_code']),
            ('country_code', row['country_code']),
            ('description', description),
            ('latlon', '%s %s' % (
                row['latitude'], row['longitude'],
            )),
            # TODO: Ignoring accuracy field for the moment
        ])
        # client.add(doc) - would work here
        queue.append(doc)
        if len(queue) >= 1000:
            client.bulkadd(queue)
            queue = []
            print "Imported %d" % count
    # Catch the remainder
    if queue:
        client.bulkadd(queue)

def make_description(row):
    description = row['place_name']
    if row['admin_name2']:
        description += ', ' + row['admin_name2']
    return description
