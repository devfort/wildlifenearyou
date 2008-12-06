# $Id$
# zzzz this needs a name
#

# Add an inner class Searchable to your model, with fields (list of django_fields) and cascades (list of strings which are Django fields that are relations to other Django model instances).
# Note that you can't have one search field multiple times (only the last one processed will be preserved).
#
# django_field is either a string (name of Django model field, use all defaults), or a dictionary.
# Within the dictionary, ``django_fields`` is either a string (again), or a callable (takes the instance, returns a list of data to index into the search field).
# ``field_name`` is the search field name (optional, auto-generated), ``config`` is an optional dictionary of configuration options (search provider dependent; currently we use xappyc)
# In your search field names, don't start with an underscore ('_') as that's reserved.
#
# We STRONGLY recommend explicitly declaring your search field names, as it makes the resultant search system more useful to users. In some cases you don't need it, but that's rare.
#
# Note that strictly you can have a callable as a django_field directly. In this case, it will be called with a parameter of None to generate the search field name (well, part of it - it only needs to be unique to the class). But don't do this, it's ugly.
#
# In normal use, you may have a single static method in your Searchable inner class, to constrain cascading in complex cases:
#
# reindex_on_cascade(sender, instance) -- defaults to True; ``sender`` is what we've just indexed which cascaded to this ``instance`` of the model
#
# If you really need, you can override most aspects of the data gathering and field generation. Generally speaking you won't have to touch this at all.
#
# get_configuration(model) -- ``model`` is fully constructed and registered, return a list of search field descriptors
# get_field_input(instance, django_field) -- return an iterable, but you almost never want to do this
# get_details(field_descriptor) -- the Searchify field descriptor, returns a tuple (django_field_list, search field name, config dictionary), you almost never want to do this either
#   (importantly, 'field_name' in the dictionary is filled out to the explicit or auto-generated search field name)
# get_index_data(instance) -- return a unique identifier (we use model ':' pk), and a dict of search field names mapping to lists of input data. We auto-create a field _TYPE which is the model name.
#
# EXAMPLE
#
# from django.db import models
#
# class Sea(models.Model):
#   name = models.CharField(null=True, blank=True, max_length=100)
#
#   class Searchable:
#     fields = [ { 'field_name': 'name', 'django_fields': ['name', lambda inst: [n.name for n in inst.narwhals], ] } ]
#
# class Narwhal(models.Model):
#   name = models.CharField(null=True, blank=True, max_length=100)
#   home = models.ForeignKey(Sea, related_name='narwhals')
#
#   class Searchable:
#     fields = [ { 'field_name': 'name', 'django_fields': ['name'] } ]
#     cascades = [ 'home' ]
#
# NASTY DETAILS
#
# When auto-generating, we use ':' to separate bits of things where possible, and '__' where we require \w only.

# FIXME: make it easy to reindex a model
# FIXME: make it easy to reindex everything
# FIXME: make it possible to index an individual model to more than one database.

# FIXME: document the new hooks
# FIXME: registering and initialising
# FIXME: document that you have to call initialise (and figure out where additional config comes from...)
# Test: the override stuff

from django.db.models.signals import post_save, pre_delete, post_delete
from django.db import models
from django.db.models import FieldDoesNotExist, BooleanField
from django.conf import settings
from djape.client import Client

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

def get_client(dbname):
    return Client(
        settings.XAPIAN_BASE_URL, dbname, settings.XAPIAN_PERSONAL_PREFIX
    )

def initialise():
    indexes = {} # Map Xapian dbname => list of fields
    for model in models.get_models():
        if not hasattr(model, 'Searchable'):
            continue
        index = getattr(model.Searchable, 'xapian_index')
        assert index, 'Searchable classes require a xapian_index property'
        indexes.setdefault(index, []).extend(get_configuration(model))
    
    # Now loop through and ensure each db exists
    for index, fields in indexes.items():
        if len(fields) == 0:
            continue # Skip this index
        client = get_client(index)
        try:
            client.newdb(fields, allow_reopen = True)
        except client.SearchClientError:
            print "Clearing database - you will need to re-index"
            client.newdb(fields, overwrite = True)
            raise
    
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
    
    client = get_client(instance.Searchable.xapian_index)
    
    if should_delete_instance(instance):
        client.delete(get_uid(instance))
        cascade_reindex(instance)
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
    client = get_index_data(instance.Searchable.xapian_index)
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
        client = get_client(instance.Searchable.xapian_index)
        # TODO: Implement client.delete
        # client.delete(get_uid(instance))
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
