from xml.etree import ElementTree as ET
import urllib
from django.conf import settings
from django.utils import simplejson

def google_geocode(q, country_code = None):
    # http://maps.google.com/maps/api/geocode/json?address=...&sensor=false
    # http://code.google.com/apis/maps/documentation/geocoding/
    args = {
        'address': q,
        'sensor': 'false',
    }
    if country_code:
        args['region'] = country_code
    json = simplejson.load(urllib.urlopen(
        'http://maps.google.com/maps/api/geocode/json?' + 
        urllib.urlencode(args)
    ))
    try:
        location = json['results'][0]['geometry']['location']
        lon = location['lng']
        lat = location['lat']
    except KeyError, IndexError:
        return None, (None, None)
    name = json['results'][0]['formatted_address']
    return name, (lat, lon)

def google_geocode_old(q, country_code = None):
    args = {
        'q': q,
        'output': 'json',
        'oe': 'utf8',
        'sensor': 'false',
        'key': settings.GOOGLE_GEOCODE_API_KEY,
    }
    if country_code:
        args['gl'] = country_code
    json = simplejson.load(urllib.urlopen(
        'http://maps.google.com/maps/geo?' + urllib.urlencode(args)
    ))
    try:
        lon, lat = json['Placemark'][0]['Point']['coordinates'][:2]
    except KeyError, IndexError:
        return None, (None, None)
    name = json['Placemark'][0]['address']
    return name, (lat, lon)

def placemaker_geocode(q):
    args = {
        'documentContent': q,
        'documentType': 'text/plain',
        'appid': settings.PLACEMAKER_API_KEY,
    }
    et = ET.parse(urllib.urlopen(
        'http://wherein.yahooapis.com/v1/document', urllib.urlencode(args))
    )
    xpath = '{NS}document/{NS}placeDetails/{NS}place'.replace(
        '{NS}', '{http://wherein.yahooapis.com/v1/schema}'
    )
    place = et.find(xpath)
    if place is None:
        return None, (None, None)
    else:
        name_xpath = '{NS}name'.replace(
            '{NS}', '{http://wherein.yahooapis.com/v1/schema}'
        )
        name = place.find(name_xpath).text
        lat_xpath = '{NS}centroid/{NS}latitude'.replace(
            '{NS}', '{http://wherein.yahooapis.com/v1/schema}'
        )
        lat = place.find(lat_xpath).text
        lon_xpath = '{NS}centroid/{NS}longitude'.replace(
            '{NS}', '{http://wherein.yahooapis.com/v1/schema}'
        )
        lon = place.find(lon_xpath).text
        return name, (lat, lon)
        
