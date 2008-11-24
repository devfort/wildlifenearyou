
from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson

import os
import re
import shutil
import xappy

def render_result_as_json(result):
    """Render a result structure to JSON and return it from the request.

    """
    return HttpResponse(simplejson.dumps(result), mimetype="text/javascript")

class SearchError(Exception):
    """Base class for errors raised and to be shown to user.

    The errtype property should contain the value to put in the "type" return
    value.

    """
    pass

class ValidationError(SearchError):
    """Raised when an invalid parameter value is supplied to the query string.

    """
    errtype = 'Validation'

class PathInUseError(SearchError):
    """Raised when there is already something at a path we want to use.
    
    When creating a database, this either means that the database is already
    there, or that there's something else in the location to be used for the
    database on the filesystem.

    """
    errtype = 'PathInUse'

class DbNotFound(SearchError):
    """Raised when no database is present at the path we expect.

    """
    errtype = 'DbNotFound'


def errchecked(fn):
    """Decorator to handle returning error descriptions

    """
    def res(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except SearchError, e:
            return {"error": str(e), "type": e.errtype}
    return res

def jsonreturning(fn):
    """Decorator to wrap function's return value as JSON.

    """
    def res(*args, **kwargs): return render_result_as_json(fn(*args, **kwargs))
    return res

def validate_params(request, constraints):
    """Validate parameters, raising ValidationError for problems.

    `constraints` is a dict of tuples, one for each field.  Unknown fields
    raise an error.

    """
    required_params = set()
    for key, constraint in constraints.iteritems():
        if constraint[0] != 0:
            required_params.add(key)

    p = {}

    for key in request.GET:
        if key in required_params:
            required_params.remove(key)

        constraint = constraints.get(key, None)
        if constraint is None:
            if re.match('\w+$', key):
                # No potentially dangerous characters
                raise ValidationError("Unknown parameter %r supplied" % key)
            else:
                raise ValidationError("Unknown parameter supplied")
        vals = request.GET.getlist(key)

        # Check we've got an acceptable number of values.
        l = len(vals)
        if l < constraint[0]:
            raise ValidationError("Too few instances of %r supplied "
                                  "(needed %d, got %d)" %
                                  (key, constraint[0], l))
        if constraint[1] is not None and l > constraint[1]:
            raise ValidationError("Too many instances of %r supplied "
                                  "(maximum %d, got %d)" %
                                  (key, constraint[1], l))

        # If not present, set vals to default
        if l == 0:
            vals = constraint[3]

        # Check the regexp pattern matches
        m = re.compile(constraint[2])
        for val in vals:
            if not m.match(val):
                raise ValidationError("Invalid parameter value for %r" % key)

        # Store the parameter for return
        p[key] = vals

    if len(required_params) != 0:
        # We trust the list of required_params not to be trying to hack us.
        raise ValidationError("Missing required parameters %s" %
                              ', '.join("'%s'" % p for p in required_params))

    return p

def get_db_path(dbname):
    return os.path.join(settings.XAPPY_DATABASE_DIR, dbname)

@jsonreturning
@errchecked
def search(request):
    """Serve a search request.

    Supported query parameters:

     - `db`: contains the name of the database.
     - `q`: contains the query string.
     - `startrank` is the rank of the start of the range of matching documents
       to return (ie, the result with this rank will be returned).  ranks start
       at 0, which represents the "best" matching document.  Defaults to 0.
     - `endrank` is the rank at the end of the range of matching documents to
       return.  This is exclusive, so the result with this rank will not be
       returned.  Defaults to 10.

    Returns

    """
    params = validate_params(request, {
                             'db': (1, 1, '^\w+$', None),
                             'q': (1, None, '^.*$', None),
                             'startrank': (0, 1, '^\d+$', ['0']),
                             'endrank': (0, 1, '^\d+$', ['10']),
                             })

    db = xappy.SearchConnection(get_db_path(params['db'][0]))
    qs = [db.query_parse(subq) for subq in qparams['q']]
    q = db.query_combine(qs)
    search_results = q.search(params['startrank'][0],
                              params['endrank'][0])

    res = {
        'db': params['db'][0],
        'matches_estimated': res.matches_estimated,
    }
    return res

@jsonreturning
@errchecked
def newdb(request):
    """Create a new database.

    Returns an error if the database already exists.

    Supported query parameters:

     - `db`: contains the name of the database.
 
    """
    params = validate_params(request, {
                             'db': (1, 1, '^\w+$', None),
                             })
    db_name = params['db'][0]
    db_path = os.path.realpath(get_db_path(db_name))

    if os.path.exists(db_path):
        raise PathInUseError("The path for '%s' is already in use" % db_path)

    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))

    db = xappy.IndexerConnection(get_db_path(params['db'][0]))
    db.add_field_action('text', xappy.FieldActions.INDEX_FREETEXT, language='en', spell=True)
    db.add_field_action('text', xappy.FieldActions.STORE_CONTENT)
    db.flush()

    return {'ok': 1}

@jsonreturning
@errchecked
def deldb(request):
    """Delete a database.

    Returns an error if the database doesn't already exist.

    Supported query parameters:

     - `db`: contains the name of the database.
 
    """

    params = validate_params(request, {
                             'db': (1, 1, '^\w+$', None),
                             })
    db_path = os.path.realpath(get_db_path(params['db'][0]))

    if not os.path.exists(db_path):
        raise DbNotFound("The path '%s' is already empty" % db_path)

    shutil.rmtree(db_path)
    return {'ok': 1}

@jsonreturning
@errchecked
def add(request):
    params = validate_params(request, {
                        'db': (1, 1, '^\w+$', None),
                        'id': (1, 1, '^\w+$', None),
                        'text': (1, None, '^\w+$', None),
                        })
    db = xappy.IndexerConnection(get_db_path(params['db'][0]))
    doc = xappy.UnprocessedDocument()
    for val in params['text']:
        doc.append('text', val)
    newid = db.add(doc)
    db.flush()
    return 
