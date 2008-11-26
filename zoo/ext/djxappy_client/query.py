
from copy import copy

class Query(object):
    """A query object.  This is composed of query parts.

    This represents arbitrarily complex queries, together with the query
    options which they support.

    """
    def __init__(self, text=None):
        """Create the query object.

        If `text` is supplied, it is treated as a text string, and is
        equivalent to setting the query definition to FreeTextQuery(text).

        """
        self.opts = {}
        self.part = None

        if text is not None:
            self.part = FreeTextQuery(text)

    def sort_by(self, field_name, ascending=True):
        """Set the field to sort by.

        """
        self.opts['sort_by'] = [(fieldname, ascending)]

    def to_params(self):
        opts = copy(self.opts)
        opts['query'] = self.part.to_params()
        return opts

class QueryPart(object):
    """A part of a query.

    This is an abstract class - use one of it's subclasses

    """
    def to_params(self):
        raise NotImplementedError('Implement this method in subclass.')

class FreeTextQuery(QueryPart):
    """A query which searches for some free text.

    """
    def __init__(self, text=None):
        """Create a query object.

        `text` is a free text, non field-specific, query string.
        For more complex queries, use one of the factory methods.

        """
        self.text = text

    def to_params(self):
        return ['freetext', self.text]

class GeoDistanceQuery(QueryPart):
    def __init__(self, centre=None):
        """Create a query object, which weights documents by distance.

        `centre` is a text representation of a latlong coordinate.

        """
        self.centre = centre

    def to_params(self):
        return ['geodistance', self.centre]


# FIXME - implement more query types
