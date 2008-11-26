import os

FILEPATH = os.path.join(
    os.path.dirname(__file__), 'data/organism_classification.tsv'
)

def import_from_file(filepath = FILEPATH):
    import csv
    reader = csv.reader(open(filepath), dialect=csv.excel_tab)
    fields = reader.next()
    for vals in reader:
        yield dict(zip(fields, vals))
