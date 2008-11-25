import random
from couchdb.client import Server, ResourceNotFound

server = Server('http://localhost:5984/')

if 'schedules' not in server:
    db = server.create('schedules')
else:
    db = server['schedules']

# Opening time

#for x in xrange(10):
#    topic = random.choice(['narwhl', 'wat', 'ceiling cat', 'monorail '])
#    
#    eid = db.create({'type': 'entry',
#                     'text': ' '.join([topic] * 3)})
#    for x in xrange(4):
#        db.create({'type': 'comment',
#                   'entry_id': eid,
#                   'text': random.choice(['lol', 'hahaha', 'wat']) + ' ' + topic })

ids = list(iter(db))

{'views': [
    
    
    ]

q = """
function(doc) {
if (typeof doc.type == 'undefined') return;
if (doc.type == 'entry')
   emit([doc._id, 0], doc.text);
else if (doc.type == 'comment')
   emit([doc.entry_id, 1], doc.text);
}"""

result = db.query(q);

for row in result:
    print row


#doc_id = db.create({'type': 'Person', 'name': 'John Doe'})
#doc = db[doc_id]
#doc['type']
#u'Person'
#doc['name']
#u'John Doe'
#del db[doc.id]
#doc.id in db
#False
#del server['python-tests']
