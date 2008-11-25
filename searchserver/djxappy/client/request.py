
import urllib2

class ClientError(Exception):
    pass

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

class XappyServiceClient(object):
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

        """
        self.base_url = base_url
        self.default_db_name = default_db_name

    def _doreq(self, path, qs=None, data=None):
        try:
            urllib2.urlopen(self.base_url + path)
        except 

    def newdb(self, format, db_name=None):
        """Format 

{
    'db_name': <dbname>,
    'fields': {
        <xappy fieldname>: {
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
        },
    },
}

        """
        pass

    def search(self, query, start_rank=None, end_rank=None, db_name=None):
        """Perform a search.

         - `query`: A Query object, containing the query to perform.
         - `start_rank`: The start rank; defaults to the server default (usually 0).
         - `end_rank`: The end rank; defaults to the server default (usually 10).

        """
        if db_name is None:
            db_name = self.default_db_name
        if db_name is None:
            raise ClientError('Missing db_name')

        req['q'] = query.query_string
        req['start_rank'] = start_rank
        req['end_rank'] = end_rank

        retval = self._doreq('search/' + db_name, 
