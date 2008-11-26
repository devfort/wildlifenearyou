
import simplejson
import urllib
import urllib2
import errors

class XappyClient(object):
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
            raise errors.SearchClientError(res['error'], res.get('type', 'Search error'))
            
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
            raise errors.SearchClientError('Missing db_name')

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
            raise errors.SearchClientError('Missing db_name')

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
            raise errors.SearchClientError('Missing db_name')

        return self._doreq('add/' + db_name, data={'doc': [doc.as_json()]})

    def bulkadd(self, docs, db_name=None):
        """Add a load of documents tothe database.

        `doc` the document (as a Document object).

        """
        if db_name is None:
            db_name = self.default_db_name
        if db_name is None:
            raise errors.SearchClientError('Missing db_name')

        return self._doreq('add/' + db_name, data={'doc': [doc.as_json() for doc in docs]})

