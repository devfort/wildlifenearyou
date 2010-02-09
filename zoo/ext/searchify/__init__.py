'''
Add an inner class Searchable to your model, with fields (list of django_fields) and cascades (list of strings which are Django fields that are relations to other Django model instances).
Note that you can't have one search field multiple times (only the last one processed will be preserved).

django_field is either a string (name of Django model field, use all defaults), or a dictionary.
Within the dictionary, ``django_fields`` is either a string (again), or a callable (takes the instance, returns a list of data to index into the search field).
``field_name`` is the search field name (optional, auto-generated), ``config`` is an optional dictionary of configuration options (search provider dependent; currently we use xappyc)
In your search field names, don't start with an underscore ('_') as that's reserved.

We STRONGLY recommend explicitly declaring your search field names, as it makes the resultant search system more useful to users. In some cases you don't need it, but that's rare.

Note that strictly you can have a callable as a django_field directly. In this case, it will be called with a parameter of None to generate the search field name (well, part of it - it only needs to be unique to the class). But don't do this, it's ugly.

In normal use, you may have a single static method in your Searchable inner class, to constrain cascading in complex cases:

reindex_on_cascade(sender, instance) -- defaults to True; ``sender`` is what we've just indexed which cascaded to this ``instance`` of the model

If you really need, you can override most aspects of the data gathering and field generation. Generally speaking you won't have to touch this at all.

get_configuration(model) -- ``model`` is fully constructed and registered, return a list of search field descriptors
get_field_input(instance, django_field) -- return an iterable, but you almost never want to do this
get_details(field_descriptor) -- the Searchify field descriptor, returns a tuple (django_field_list, search field name, config dictionary), you almost never want to do this either
  (importantly, 'field_name' in the dictionary is filled out to the explicit or auto-generated search field name)
get_index_data(instance) -- return a unique identifier (we use model ':' pk), and a dict of search field names mapping to lists of input data. We auto-create a field _TYPE which is the model name.

EXAMPLE

from django.db import models

class Sea(models.Model):
  name = models.CharField(null=True, blank=True, max_length=100)

  class Searchable:
    fields = [ { 'field_name': 'name', 'django_fields': ['name', lambda inst: [n.name for n in inst.narwhals], ] } ]

class Narwhal(models.Model):
  name = models.CharField(null=True, blank=True, max_length=100)
  home = models.ForeignKey(Sea, related_name='narwhals')

  class Searchable:
    fields = [ { 'field_name': 'name', 'django_fields': ['name'] } ]
    cascades = [ 'home' ]

NASTY DETAILS

When auto-generating, we use ':' to separate bits of things where possible, and '__' where we require \w only.

FIXME: make it easy to reindex a model (including 'cheap' where we don't delete everything for that model first)
FIXME: make it easy to reindex everything
FIXME: it's easy to accidentally delete the database after initialisation happens; we should provide a CLEAR DATABASE function (used by reindexing, above) which safely clears and ensures that the database has appropriate configuration at the end of things
FIXME: document the query() method added to managers
FIXME: registering and initialising so we're not bound to Djape. (Possibly even write something to tie into Lucene/Solr or similar.)
FIXME: other FIXMEs ;-)

FIXME: drop xapian_index
FIXME: check any other changes made by Simon and/or Richard
FIXME: document the new hooks (and move to docstring throughout)
FIXME: document that you have to call initialise (and figure out where additional config comes from...)

TODO: make it possible to index an individual model to more than one database.
TODO: reverse cascades, so you can put searchable stuff into your Profile model, but have it index stuff from the User.
Test: the override stuff
'''

from django.db.models.signals import post_save, pre_delete, post_delete
from django.db import models
from django.db.models import FieldDoesNotExist, BooleanField
from django.conf import settings
from djape.client import Client, Query, FreeTextQuery

class TestClient:
    def newdb(self, fields, dbname):
        print 'init ' + dbname
        print 'config ' + str(fields)
        
    class Document:
        def __init__(self):
            self.d = {}
            self.id = None
            
        def extend(self, data):
            self.d.update(data)
        
    def add(self, doc):
        print 'index %s: %s' % (doc.id, str(doc.d))
        
    def delete(self, uid):
        print 'delete ' + uid

def get_client(dbname_or_model):
    if not isinstance(dbname_or_model, str):
        dbname = get_index(dbname_or_model)
    else:
        dbname = dbname_or_model
    return Client(
        settings.XAPIAN_BASE_URL, dbname, settings.XAPIAN_PERSONAL_PREFIX
    )

def make_searcher(manager, model):
    index = get_index(model)
    if not index:
        # FIXME: this isn't done properly... it can't respond to the same methods etc. as QueryResult, below
        def search(query=None, num=0):
            return []
        return search

    c = get_client(index)
    def search(query=None, num=0):
        class QueryResult:
            def __init__(self, results):
                self.results = results
                search_ids = [ item['id'] for item in results['items'] ]
                self._result_ids = []
                self._deets = {}
                for item in results['items']:
                    search_id = item['id']
                    model_key, id = search_id.split(':')
                    if model_key != model.__name__:
                        # FIXME: not right!
                        # Either we need to get this right, or we could filter the query through a boolean to restrict to
                        # this model in the first place. The latter would work better, but requires some thought. (In particular,
                        # semi-constructing queries like this unsettles Richard, so there's probably a reason to avoid it.)
                        #continue
                        pass
                    self._result_ids.append(id)
                    self._deets[id] = item
                self._bulk = manager.in_bulk(self._result_ids)

            # From djape, we get: matches_lower_bound, doc_count, matches_upper_bound, db_name, _orig_xapian_query, elapsed, has_more_results, matches_estimated
            # We really care about everything except _orig_xapian_query (which you'd have to extract in code rather than templates anyway).
            def __getattr__(self, key):
                """Provide .-access to aspects of the result. eg: q.doc_count (providing the search provider returns doc_count)."""
                return self.results.get(key)

            def __len__(self):
                return len(self._result_ids)
            
            def __iter__(self):
                """
                Iterate over the results, in the order they were in the result set.
                Return a decorated object, ie the Django model instance with an extra attribute (default 'match') containing match details (you mostly care about 'rank', if provided).
                """
                for key in self._result_ids:
                    obj = self._bulk[long(key)]
                    # From djape we get: data (dict of field->data pairs), id, rank
                    # We only really care about rank at this stage, as we've pulled out the object.
                    if hasattr(model.Searchable, 'match_details_attribute'):
                        match_attr = model.Searchable.match_details_attribute
                    else:
                        match_attr = 'match'
                    if match_attr is not None:
                        setattr(obj, match_attr, self._deets[str(obj.pk)])
                    yield obj
        
        results = c.search(Query(query), end_rank=num)
        return QueryResult(results)
    return search

def get_index(model_or_inst):
    index = None
    if hasattr(model_or_inst.Searchable, 'index'):
        index = getattr(model_or_inst.Searchable, 'index')
    elif hasattr(model_or_inst.Searchable, 'xapian_index'):
        index = getattr(model_or_inst.Searchable, 'xapian_index')
    # The following is not true: you may want to configure aspects of searchify on a non-indexed class (eg: cascades)
    #assert index, 'Searchable classes require an index property (or xapian_index for temporary bc)'
    return index

def initialise():
    indexes = {} # Map Xapian dbname => list of fields
    imodels = []
    for model in models.get_models():
        if not hasattr(model, 'Searchable'):
            continue
        index = get_index(model)
        if index!=None:
            indexes.setdefault(index, []).extend(get_configuration(model))
            imodels.append(model)
    
    # Now loop through and ensure each db exists
    for index, fields in indexes.items():
        if len(fields) == 0:
            continue # Skip this index
        client = get_client(index)
        try:
            client.newdb(fields, allow_reopen = True)
        except client.SearchClientError:
            print "Clearing database '%s' - you will need to re-index" % index
            client.newdb(fields, overwrite = True)
            raise
    
    # Finally, go back over the models adding searchers to the default manager
    for model in imodels:
        if hasattr(model.Searchable, 'managers'):
            managers = getattr(model.Searchable, 'managers')
        else:
            managers = ['objects']
        for manager in managers:
            manager = getattr(model, manager)
            if hasattr(model.Searchable, 'query'):
                manager.query = getattr(model.Searchable, 'query')
            else:
                manager.query = make_searcher(manager, model)
    
    # Set up the global signal hooks
    post_save.connect(index_hook)
    pre_delete.connect(delete_hook)

def index_hook(sender, **kwargs):
    index_instance(kwargs['instance'])

def delete_hook(sender, **kwargs):
    delete_instance(kwargs['instance'])

def post_delete_hook(instance):
    def hook(sender, **kwargs):
        if kwargs['instance']==instance:
            cascade_reindex(kwargs['instance'])
            post_delete.disconnect(hook)
    return hook

def index_instance(instance):
    if not hasattr(instance, 'Searchable'):
        return False

    # first, check should_delete_instance for situations where we *mark* as
    # deleted rather than deleting in the ORM/database
    # (eg: a deleted boolean field)

    index = get_index(instance)
    if not index:
        cascade_reindex(instance)
        return
    client = get_client(index)
    
    if should_delete_instance(instance):
        client.delete(get_uid(instance))
    else:
        dret = get_index_data(instance)
        if dret!=None:
            (ident, fielddata) = dret
            doc = client.Document()
            doc.extend(fielddata)
            doc.id = ident
            client.add(doc)

    cascade_reindex(instance)

def cascade_reindex(instance):
    if not hasattr(instance, 'Searchable') or \
        not hasattr(instance.Searchable, 'cascades'):
        return
    for descriptor in instance.Searchable.cascades:
        if isinstance(descriptor, str):
            cascade_inst = getattr(instance, descriptor)
            if hasattr(cascade_inst, 'Searchable'):
                if hasattr(cascade_inst.Searchable, 'reindex_on_cascade'):
                    if not cascade_inst.Searchable.reindex_on_cascade(
                        instance, cascade_inst
                    ):
                        continue
                index_instance(cascade_inst)
                # ie: recurse through this function to get recursion, yay!

def delete_instance(instance):
    if hasattr(instance, 'Searchable'):
        index = get_index(instance)
        if index:
            client = get_client(index)
            client.delete(get_uid(instance))
    post_delete.connect(post_delete_hook(instance))

# UTILITY FUNCTIONS
#
# These are the default behaviours for the various steps in the above strategy (some are actually defaults for steps in strategies in functions below).

# Should we delete this instance? By default, we look for a BooleanField called ``deleted``.
# Can be overridden.
def should_delete_instance(instance):
    if not hasattr(instance, 'Searchable'):
        return False
    if hasattr(instance.Searchable, 'should_delete_instance'):
        return instance.Searchable.should_delete_instance(instance)
    try:
        fielddef = instance._meta.get_field('deleted')
        if isinstance(fielddef, BooleanField):
            return instance.deleted
    except FieldDoesNotExist:
        return False

# Get the configuration for a particular model by pulling in details from Searchable.fields
# Can be overridden.
def get_configuration(model):
    # return a list of xappy field descriptors for this model
    if not hasattr(model, 'Searchable'):
        return []
    if hasattr(model.Searchable, 'get_configuration'):
        return model.Searchable.get_configuration(model)
    if not hasattr(model.Searchable, 'fields'):
        return []
    fields = []
    for field in model.Searchable.fields:
        (django_field_list, search_fieldname, config) = get_details(model, field)
        config['field_name'] = search_fieldname
        fields.append(config)
    return fields

# Return (django_field_list, search field name, config) for a particular search field (which is a string, dict or possibly callable).
# Performs auto-generation of search field names.
# Can be over-ridden.
def get_details(instance_or_model, field):
    if hasattr(instance_or_model, 'Searchable') and hasattr(instance_or_model.Searchable, 'get_details'):
        return instance_or_model.Searchable.get_details(field)
    if type(field) is dict:
        django_field_list = field['django_fields']
        xappy_fieldname = field.get('field_name')
    else:
        django_field_list = [field]
        xappy_fieldname = None
    if xappy_fieldname == None:
        if isinstance(django_field_list[0], str):
            field_specific_name = django_field_list[0]
        elif callable(django_field_list[0]):
            field_specific_name = django_field_list[0](None)
        xappy_fieldname = filter(lambda x: x.isalpha(), field_specific_name)
    # auto-detect index type (eg: date) based on field type (if FIXME: django_field_list allows us to figure it out?)
    if type(field) is dict:
        return (django_field_list, xappy_fieldname, field.get('config', {}))
    else:
        return (django_field_list, xappy_fieldname, {})

# Given a single Django field descriptor (string or callable), generate a list of data to input to the search field.
# Can be overridden.
def get_field_input(instance, django_field):
    #print 'get_field_input ' + str(instance) + ', ' + django_field
    if hasattr(instance, 'Searchable') and hasattr(instance.Searchable, 'get_field_input'):
        return instance.Searchable.get_field_input(instance, django_field)
    # must return an iterable; django_field is str (name) or callable
    if isinstance(django_field, str):
        #print 'trying as str'
        #print '.name = %s' % instance.name
        #print 'getattr(,"name") = %s' % getattr(instance, 'name')
        val = getattr(instance, django_field)

        def datetime_converter(d):
            return unicode(d.date())

        converters = { models.DateTimeField: datetime_converter }
        field = instance._meta.get_field(django_field).__class__
        if val == None:
            return []
        if field in converters:
            val = converters[field](val)
        else:
            val = unicode(val)
        return [val]
    elif callable(django_field):
        return django_field(instance)
    else:
        return []

# Generate a system-wide persistent uid for this instance.
# Can be overridden.
def get_uid(instance):
    if not hasattr(instance,'Searchable'):
        return None
    if hasattr(instance.Searchable, 'get_uid'):
        return instance.Searchable.get_uid(instance)
    else:
        return '%s.%s:%s' % (
            instance._meta.app_label, instance._meta.object_name, instance.pk
        )

# Given a Django model instance, return a unique identifier and a dict of search fields mapping to list of data.
# Can be overridden.
def get_index_data(instance):
    if not hasattr(instance,'Searchable'):
        return None
    if hasattr(instance.Searchable, 'get_index_data'):
        return instance.Searchable.get_index_data(instance)
    if not hasattr(instance.Searchable, 'fields'):
        return None
    fields = instance.Searchable.fields
    
    # ``_TYPE`` field based on model name (so we can search just a particular model)
    outfields = { '_TYPE': [instance._meta.module_name] }
        
    for field in fields:
        (django_field_list, xappy_fieldname, xappy_config) = get_details(instance, field)
        interim_data = map(lambda x: get_field_input(instance, x), django_field_list)
        #print '>>>' + str(interim_data)
        outfields[xappy_fieldname] = reduce(lambda x,y: x + y, interim_data)
    
    return (get_uid(instance), outfields)
