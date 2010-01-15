from django.core import urlresolvers
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db import connection
from zoo.shortcuts import render

intro_text = """Named URL patterns for the {% url %} tag
========================================

e.g. {% url pattern-name %}
or   {% url pattern-name arg1 %} if the pattern requires arguments

"""
def show_url_patterns(request):
    patterns = get_named_patterns()
    r = HttpResponse(intro_text, content_type = 'text/plain')
    longest = max([len(pair[0]) for pair in patterns])
    for key, value in patterns:
        r.write('%s %s\n' % (key.ljust(longest + 1), value))
    return r

def get_named_patterns():
    "Returns list of (pattern-name, pattern) tuples"
    resolver = urlresolvers.get_resolver(None)
    patterns = sorted([
        (key, value[0][0][0])
        for key, value in resolver.reverse_dict.items()
        if isinstance(key, basestring)
    ])
    return patterns

@login_required
def show_innodb_status(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    
    c = connection.cursor()
    c.execute('show engine innodb status')
    info = c.fetchone()[-1]
    row_operations = info.split('ROW OPERATIONS')[1]
    lines = row_operations.split('\n')
    interesting_lines = lines[2:-4]
    interesting_lines.reverse()
    
    return render(request, 'debug/show_innodb_status.html', {
        'info': info,
        'interesting_lines': interesting_lines,
    })
