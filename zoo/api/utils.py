from django.http import HttpResponse
from django.utils import simplejson
import re

callback_re = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]+$')

def api_response(request, status_code, info):
    info['status'] = status_code
    if request.GET.get('format', '') == 'html':
        return HttpResponse(
            '<html><head><title>API response</title></head><body><pre>' + 
            simplejson.dumps(info, indent=2) + 
            '</pre></body></html>',
            content_type='text/html; charset=utf8'
        )
    
    content_type = 'application/javascript; charset=utf8'
    if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
        content_type = 'application/json; charset=utf8'
    
    json = simplejson.dumps(info, indent=2)
    callback = request.GET.get('callback', '')
    if callback_re.match(callback):
        json = '%s(%s)' % (callback, json)
        status_code = 200
        content_type = 'application/javascript; charset=utf8'
    
    response = HttpResponse(
        json,
        content_type=content_type, status=status_code
    )
    response['Vary'] = 'Accept'
    return response

def api_date(dt):
    if dt:
        return dt.strftime('%Y-%m-%d')
    else:
        return ''

def api_datetime(dt):
    if dt:
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return ''
