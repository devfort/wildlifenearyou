
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

