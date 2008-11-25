
import simplejson
import urllib
import urllib2

class SearchClientError(Exception):
    def __init__(self, msg, errtype):
        self.msg = msg
        self.errtype = errtype

    def __str__(self):
        return "%s: %s" % (self.errtype, self.msg)

class Query(object):
    """A query object.

    This represents arbitrarily complex queries, together with the query
    options which they support.

    """
    def __init__(self, query_string=None):
        """Create a query object.

        `query_string` is a free text, non field-specific, query string.
        For more complex queries, use one of the factory methods.

        """
        self.query_string = query_string

    # FIXME - implement more factory methods!

class Field(object):
    """An instance of a Field in a document.

    """

    # Use __slots__ because we're going to have very many Field objects in
    # typical usage.
    __slots__ = 'name', 'value'

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return 'Field(%r, %r)' % (self.name, self.value)

class Document(object):
    """A document to be passed to the indexer.

    This represents an item to be stored in the search engine.

    Note that some information in a Document will not be represented in the
    index: therefore, it is not possible to retrieve a full Document from the
    search engine index.

    A document is a simple container with two attributes:

     - `fields` is a list of Field objects, or an iterator returning Field
       objects.
     - `id` is a string holding a unique identifier for the document (or
       None to get the database to allocate a unique identifier automatically
       when the document is added).

    It also has some convenience methods to assist in building up the contents.

    """

    __slots__ = 'id', 'fields',
    def __init__(self, id=None, fields=None):
        self.id = id
        if fields is None:
            self.fields = []
        else:
            self.fields = fields

    def __repr__(self):
        return 'Document(%r, %r)' % (self.id, self.fields)

    def append(self, *args, **kwargs):
        """Append a field to the document.

        This may be called with a Field object, in which case it is the same as
        calling append on the "fields" member of the Document.
        
        Alternatively. it may be called with a set of parameters for creating a
        Field object, in which case such a Field object is created (using the
        supplied parameters), and appended to the list of fields.

        """
        if len(args) == 1 and len(kwargs) == 0:
            if isinstance(args[0], Field):
                self.fields.append(args[0])
                return
        # We assume we just had some arguments for appending a Field.
        self.fields.append(Field(*args, **kwargs))

    def extend(self, fields):
        """Append a sequence or iterable of fields or groups to the document.

        This is simply a shortcut for adding several Field objects to the
        document, by calling `append` with each item in the list of fields
        supplied.

        `fields` should be a sequence containing items which are either Field
        objects, or sequences of parameters for creating Field objects.

        """
        for field in fields:
            if isinstance(field, Field):
                self.fields.append(field)
            else:
                self.fields.append(Field(*field))

    def as_json(self):
        """Return a JSON represenation of the document.

        Probably not the best implementation currently - lots of copying.

        """
        req = {
            'id': self.id,
            'data': [[field.name, field.value] for field in self.fields],
        }
        return simplejson.dumps(req)

class SearchClient(object):
    """A client for the Xappy webservice.

    """

    def __init__(self, base_url, default_db_name=None):
        """Create a client.
        
        Doesn't make a connection to anything until it's used.

         - `base_url`: the base URL to connect to the service on.  Should end
           with a /.
         - `default_db_name`: the default database name to use.  (This is
           merely a convenience - this may be used instead of supplying the
           name to every call.)

        The time taken for the last call made is available in the
        `last_elapsed_time` member (this is set to None if not available).

        """
        self.base_url = base_url
        self.default_db_name = default_db_name

        self.last_elapsed_time = None

    def _doreq(self, path, qs=None, data=None):
        """Perform a request to path.

        If qs is supplied, format as a querystring, and append to the path
        used.  qs should be a dictionary of parameters.  parameter values may
        be strings, or lists (in which latter case, multiple instances will be
        sent).

        If data is supplied it is a dictionary of fields which are sent as a POST request.

        """
        if qs is not None:
            args = []
            for field, vals in qs.iteritems():
                if vals is None:
                    continue
                if isinstance(vals, basestring):
                    vals = [vals]
                vals = filter(None, vals)
                args.append((field, vals))
            path += '?' + urllib.urlencode(args, doseq=1)

        if data is None:
            fd = urllib2.urlopen(self.base_url + path)
        else:
            print data
            data = urllib.urlencode(data, doseq=1)
            print (self.base_url + path, data)
            fd = urllib2.urlopen(self.base_url + path, data)
        res = fd.read()
        fd.close()

        res = simplejson.loads(res)
        if 'elapsed' in res:
            self.last_elapsed_time = res['elapsed']
        else:
            self.last_elapsed_time = None
        if 'error' in res:
            raise SearchClientError(res['error'], res.get('type', 'Search error'))
            
        return res

    def search(self, query, start_rank=None, end_rank=None, db_name=None):
        """Perform a search.

         - `query`: A Query object, containing the query to perform.
         - `start_rank`: The start rank; defaults to the server default (usually 0).
         - `end_rank`: The end rank; defaults to the server default (usually 10).

        FIXME: document return type - perhaps wrap in an object

        """
        if db_name is None:
            db_name = self.default_db_name
        if db_name is None:
            raise Invalid('Missing db_name')

        req = {
            'q': query.query_string,
            'start_rank': start_rank,
            'end_rank': end_rank,
        }

        return self._doreq('search/' + db_name, qs=req)

    def listdbs(self):
        """Get a list of the available databases.

        Returns a list of strings, representing the database names.

        """
        res = self._doreq('listdbs')
        return res['db_names']

    def newdb(self, fields, db_name=None):
        """Create a new database.
        
        Returns an error if the database already exists.

         - `fields` is a list of parameters for the database configuration.
           Each item in the list is a dictionary containing details about the
           configuration for that field in xappy.  The field_name specified in
           each dictionary must be unique (ie, can't appear in multiple entries
           in the list).

        The dictionaries contain the following:

        {
            'field_name': # fieldname (required)
            'type':  # One of 'text', 'date', 'geo', 'float' (default=text)
            'store': # boolean (default=False), whether to store in document data (for 'display')
            'spelling_word_source': # boolean (default=False), whether to use for build the spelling dictionary
            'collapsible': # boolean (default=False), whether to use for collapsing
            'sortable': # boolean (default=False), whether to allow sorting on the field
            'range_searchable': # boolean (default=False), whether to allow range searches on the field
            'is_document_weight': # boolean (default=False), whether the field value can be used for document weighting

            'freetext': {
                # If present (even if empty), field is indexed for free text searching
                'language': # string (2 letter ISO lang code) (default None) - if missing or None, no language specific stuff is done
                'term_frequency_multiplier': # int (default 1) - must be positive or zero - multiplier for term frequency, increases term frequency by the given multipler to increase its weighting
                'enable_phrase_search': # boolean (default True) - whether to allow phrase searches on this field
                'index_groups': [
                    # Index groupings to index this field.  Defaults to containing '_FIELD_INDEX' and '_GENERAL_INDEX'
                    '_FIELD_INDEX': magic value to say to include in a index grouping specific to just this field
                    '_GENERAL_INDEX': index in the general index (used for non-field specific searches by default)
                    # Note - currently (Nov 2008) no other index groups are supported
                ]
            },

            'exact': {
                # If present (even if empty), search is indexed for exact text searching
                'index_groups': [
                    # Index groupings to index this field.  Defaults to containing '_FIELD_INDEX'
                    '_FIELD_INDEX': magic value to say to include in a index grouping specific to just this field
                    # Note - currently (Nov 2008) no other index groups are supported
                ]
            },

            # Note - only one of "freetext" and "exact" may be supplied
        }

        """
        if db_name is None:
            db_name = self.default_db_name
        if db_name is None:
            raise SearchClientError('Missing db_name')

        req = {
            'db_name': db_name,
            'fields': simplejson.dumps(list(fields)),
        }

        return self._doreq('newdb', data=req)

    def deldb(self, db_name=None):
        """Delete the database.

        """
        if db_name is None:
            db_name = self.default_db_name
        if db_name is None:
            raise SearchClientError('Missing db_name')

        req = {
            'db_name': db_name,
        }

        return self._doreq('deldb', data=req)

    def add(self, doc, db_name=None):
        """Add a document to the database.

        `doc` the document (as a Document object).

        """
        if db_name is None:
            db_name = self.default_db_name
        if db_name is None:
            raise SearchClientError('Missing db_name')

        return self._doreq('add/' + db_name, data={'doc': [doc.as_json()]})

    def bulkadd(self, docs, db_name=None):
        """Add a load of documents tothe database.

        `doc` the document (as a Document object).

        """
        if db_name is None:
            db_name = self.default_db_name
        if db_name is None:
            raise SearchClientError('Missing db_name')

        return self._doreq('add/' + db_name, data={'doc': [doc.as_json() for doc in docs]})

