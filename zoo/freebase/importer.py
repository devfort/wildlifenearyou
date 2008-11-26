import os
from djape.client import Client, Document
from django.conf import settings

FILEPATH = os.path.join(
    os.path.dirname(__file__), 'data/organism_classification.tsv'
)

def import_from_file(filepath = FILEPATH):
    import csv
    reader = csv.reader(open(filepath), dialect=csv.excel_tab)
    fields = reader.next()
    for vals in reader:
        yield dict(zip(fields, vals))

def import_into_xapian():
    client = Client(settings.XAPIAN_BASE_URL, settings.XAPIAN_SPECIES_DB)
    client.deldb() #if we want to delete it first
    client.newdb([{
        'field_name': 'common_name',
        'store': True,
        'freetext': {'language': 'en'} # language used for stemming
    }, {
        'field_name': 'scientific_name',
        'store': True,
        'freetext': {}
    }])
    # We have a database!
    
    # Now we create documents
    queue = []
    count = 0
    for row in import_from_file():
        if not row['scientific_name']:
            continue
        count += 1
        doc = Document()
        # doc.id = 'X' will over-ride auto ID /AND/ cause replace if exists
        doc.extend([
            ('common_name', row['name']),
            ('scientific_name', row['scientific_name']),
        ])
        # client.add(doc) - would work here
        queue.append(doc)
        if len(queue) >= 10000:
            client.bulkadd(queue)
            queue = []
            print "Imported %d" % count
    # Catch the remainder
    if queue:
        client.bulkadd(queue)
