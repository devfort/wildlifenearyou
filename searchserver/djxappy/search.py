
from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson

import dircache
import os
import re
import shutil
import time
import xappy

def render_result_as_json(result):
    """Render a result structure to JSON and return it from the request.

    """
    return HttpResponse(simplejson.dumps(result, indent=4),
                        mimetype="text/javascript")

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

def timed(fn):
    """Decorator to time function and insert time into result

    """
    def res(*args, **kwargs): 
        start = time.time()
        retval = fn(*args, **kwargs)
        retval['elapsed'] = time.time() - start
        return retval
    return res

def validate_param(key, vals, minreps, maxreps, pattern, default):
    """Validate a particular parameter.

    """
    l = len(vals)

    # If not present, and there is a default, set vals to default
    print l, vals, default
    if l == 0 and default is not None:
        vals = default

    # Check we've got an acceptable number of values.
    if l < minreps:
        raise ValidationError("Too few instances of %r supplied "
                              "(needed %d, got %d)" %
                              (key, minreps, l))
    if maxreps is not None and l > maxreps:
        raise ValidationError("Too many instances of %r supplied "
                              "(maximum %d, got %d)" %
                              (key, maxreps, l))

    # Check the regexp pattern matches
    m = re.compile(pattern)
    for val in vals:
        if not m.match(val):
            raise ValidationError("Invalid parameter value for %r" % key)

    return vals

def validate_params(request, constraints):
    """Validate parameters, raising ValidationError for problems.

    `constraints` is a dict of tuples, one for each field.  Unknown fields
    raise an error.

    """
    p = {}

    # Check for missing parameters - add if they have a default, otherwise give
    # and error.
    missing_params = set()
    for key, constraint in constraints.iteritems():
        if constraint[3] is not None:
            if key not in request.GET:
                p[key] = constraint[3]
        else:
            # check for missing params
            if constraint[0] > 0 and key not in request.GET:
                missing_params.add(key)

    if len(missing_params) != 0:
        # We trust the list of missing_params not to be trying to hack us.
        raise ValidationError("Missing required parameters %s" %
                              ', '.join("'%s'" % p for p in missing_params))

    for key in request.GET:
        constraint = constraints.get(key, None)
        if constraint is None:
            if re.match('\w+$', key):
                # No potentially dangerous characters
                raise ValidationError("Unknown parameter %r supplied" % key)
            else:
                raise ValidationError("Unknown parameter supplied")
        p[key] = validate_param(key, request.GET.getlist(key), *constraint)

    return p

def get_db_path(dbname):
    return os.path.join(settings.XAPPY_DATABASE_DIR, dbname)

@jsonreturning
@timed
@errchecked
def search(request, db_name):
    """Serve a search request.

     - `db_name`: contains the name of the database.

    Supported query parameters:

     - `q`: contains the query string.
     - `startrank` is the rank of the start of the range of matching documents
       to return (ie, the result with this rank will be returned).  ranks start
       at 0, which represents the "best" matching document.  Defaults to 0.
     - `endrank` is the rank at the end of the range of matching documents to
       return.  This is exclusive, so the result with this rank will not be
       returned.  Defaults to 10.

    Returns some JSON:

     - `db`: database name:
     - `items`:
        list of search result items (in rank order, best first). Each item is
        dict of:
        - `rank`: rank of result - 0 is best
        - `id`: id of result
        - `data`: data of result, which is a dict, keyed by name, contents is a
          list of values.
     - `matches_lower_bound`: lower bound on number of matches.
     - `matches_estimated`: estimated number of matches.
     - `matches_upper_bound`: upper bound on number of matches.
     - `doccount`: number of documents in database.

    """
    params = validate_params(request, {
                             'q': (0, None, '^.*$', []),
                             'startrank': (1, 1, '^\d+$', ['0']),
                             'endrank': (1, 1, '^\d+$', ['10']),
                             'spellcorrect': (0, 1, '^never|auto|always$', ['auto']),
                             })

    db = xappy.SearchConnection(get_db_path(db_name))

    retval = {
        'db': db_name,
        'doccount': db.get_doccount(),
    }

    if len(params['q']) == 0:
        q = db.query_all()
    else:
        qs = [db.query_parse(subq) for subq in params['q']]
        q = db.query_composite(xappy.SearchConnection.OP_OR, qs)
    res = q.search(int(params['startrank'][0]),
                   int(params['endrank'][0]))

    if len(res) == 0:
        if len(params['q']) != 0:
            # Try spell correcting
            corrected_q = [db.spell_correct(subq) for subq in params['q']]
            qs = [db.query_parse(subq) for subq in corrected_q]
            q = db.query_composite(xappy.SearchConnection.OP_OR, qs)

            res = q.search(int(params['startrank'][0]),
                           int(params['endrank'][0]))
            if len(res) != 0:
                retval['spellcorrected'] = True
                retval['spellcorr_q'] = corrected_q

    items = ({
             'rank': (item.rank),
             'id': (item.id),
             'data': (item.data),
             }
             for item in res)

    retval.update({
        'items': list(items),
        'matches_lower_bound': res.matches_lower_bound,
        'matches_estimated': res.matches_estimated,
        'matches_upper_bound': res.matches_upper_bound,
    })
    return retval

@jsonreturning
@timed
@errchecked
def listdbs(request):
    """Get a list of available databases.

    """
    return {'dbs': dircache.listdir(settings.XAPPY_DATABASE_DIR)}

@jsonreturning
@timed
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
@timed
@errchecked
def deldb(request, db_name):
    """Delete a database.

    Returns an error if the database doesn't already exist.

    Supported query parameters:

     - `db`: contains the name of the database.
 
    """

    db_path = os.path.realpath(get_db_path(db_name))

    if not os.path.exists(db_path):
        raise DbNotFound("The path '%s' is already empty" % db_path)

    shutil.rmtree(db_path)
    return {'ok': 1}

@jsonreturning
@timed
@errchecked
def add(request, db_name):
    params = validate_params(request, {
                        'id': (0, 1, '^\w+$', []),
                        'text': (1, None, '^.*$', None),
                        })
    db = xappy.IndexerConnection(get_db_path(db_name))
    doc = xappy.UnprocessedDocument()
    for val in params['text']:
        doc.append('text', val)
    if len(params['id']) > 0:
        doc.id = params['id'][0]
    newid = db.add(doc)
    db.flush()
    return {'ok': 1, 'id': newid, 'doccount': db.get_doccount()}

