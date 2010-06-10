from django.http import HttpResponse
from django.utils import simplejson
from django.conf import settings
from xml.etree import ElementTree as ET
import re, yaml

callback_re = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]+$')

def indent(elem, level=0):
    # http://effbot.org/zone/element-lib.htm
    i = '\n' + level * '  '
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + '  '
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def json_to_xml(json):
    el = json_to_element(json)
    indent(el)
    return ET.tostring(el)

def json_to_element(json):
    if isinstance(json, bool):
        el = ET.Element('bool')
        el.text = str(json)
        return el
    if isinstance(json, basestring):
        el = ET.Element('str')
        el.text = json
        return el
    if isinstance(json, int):
        el = ET.Element('int')
        el.text = str(json)
        return el
    if isinstance(json, float):
        el = ET.Element('int')
        el.text = str(json)
        return el
    if json is None:
        return ET.Element('null')
    if isinstance(json, (list, tuple)):
        el = ET.Element('list')
        for item in json:
            inner_el = ET.Element('item')
            inner_el.append(json_to_element(item))
            el.append(inner_el)
        return el
    if isinstance(json, dict):
        el = ET.Element('dict')
        for key, value in json.items():
            inner_el = ET.Element('entry')
            inner_el.attrib['key'] = key
            inner_el.append(json_to_element(value))
            el.append(inner_el)
        return el
    assert False, 'Cannot XML serialize object of type %s' % type(json)

def api_response(request, status_code, result, ok=True):
    info = {
        'ok': ok,
        'status': status_code,
        'version': settings.OUR_API_VERSION,
        'result': result,
    }
    format = request.GET.get('format', '')
    if format not in ('html', 'xml', 'json', 'yaml', ''):
        return HttpResponse('Unknown format', content_type = 'text/plain')
    
    if format == 'html':
        return HttpResponse(
            '<html><head><title>API response</title></head><body><pre>' + 
            simplejson.dumps(info, indent=2) + 
            '</pre></body></html>',
            content_type='text/html; charset=utf8'
        )
    
    if format == 'xml':
        return HttpResponse(
            json_to_xml(info),
            content_type='application/xml; charset=utf8', status=status_code
        )
    
    if format == 'yaml':
        return HttpResponse(
            yaml.safe_dump(info),
            content_type='text/plain; charset=utf8', status=status_code
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
