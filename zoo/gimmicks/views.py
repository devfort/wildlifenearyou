from django.shortcuts import get_object_or_404, render_to_response as render
from models import Gimmick
from places.models import Place
from animals.models import Species

from zoo.search.geocoders import google_geocode as google_geocode_original
import geopy, geopy.distance

from django.utils.safestring import mark_safe
from django.core.cache import cache

import datetime, md5

def google_geocode(q, country_code = None, is_latlon=False):
    key = md5.new('google-geocode:%s:%s' % (q, country_code)).hexdigest()
    cached = cache.get(key)
    if cached is not None:
        return cached
    cached = google_geocode_original(q, country_code)
    timeout = 24 * 60 * 60
    if is_latlon:
        timeout = 5 * 60
    cache.set(key, cached, timeout)
    return cached

def gimmick(request, domain):
    gimmick = get_object_or_404(Gimmick, domain = domain)
    
    # Suggest get from google.loader.ClientLocation.address.country_code
    q = request.GET.get('q', '').strip()
    country_code = request.GET.get('cc', '').strip()
    
    lat = request.GET.get('lat', '').strip()
    lon = request.GET.get('lon', '').strip()
    
    if (not lat or not lon) and q:
        name, (lat, lon) = google_geocode(q, country_code = country_code)
        return gimmick_results(request, gimmick, name, lat, lon)
    elif (lat and lon):
        name, (ignore1, ignore2) = google_geocode(
            '%s,%s' % (lat, lon), is_latlon=True
        )
        return gimmick_results(request, gimmick, name, lat, lon)
    else:
        return render('gimmicks/index.html', {
            'gimmick': gimmick,
            'request_path': request.path,
        })

def gimmick_results(request, gimmick, name, lat, lon):
    all_possible_places = list(Place.objects.filter(
        sighting__species__gimmick = gimmick
    ).extra(
        select = {
            'animals_species_id': 'animals_species.id'
        }
    ).values('pk', 'longitude', 'latitude', 'animals_species_id'))
    
    point1 = geopy.Point(latitude = lat, longitude = lon)
    
    for place in all_possible_places:
        place['point'] = geopy.Point(
            latitude = place['latitude'],
            longitude = place['longitude']
        )
        place['distance'] = geopy.distance.VincentyDistance(
            point1, place['point']
        )
    
    all_possible_places.sort(key = lambda p: p['distance'].km)
    
    results = []
    seen_place_ids = set()
    
    # Now load the actual ORM objects
    place_pks = set([p['pk'] for p in all_possible_places])
    places = Place.objects.select_related(
        'country'
    ).in_bulk(list(place_pks))
    species_pks = set([p['animals_species_id'] for p in all_possible_places])
    species = Species.objects.in_bulk(list(species_pks))
    
    for place in all_possible_places:
        if place['pk'] in seen_place_ids:
            continue
        
        if len(results) >= 5:
            break
        
        seen_place_ids.add(place['pk'])
        results.append(place)
        
        place['place'] = places[place['pk']]
        place['species'] = species[place['animals_species_id']]
        info = place['place'].species_info(place['species'])
        place.update(info)
        if not place['photo']:
            place['photo'] = place['species'].photo()
        num_sightings = place['num_sightings']
        if num_sightings == 1:
            num_spottings = 'once'
        elif num_sightings == 2:
            num_spottings = 'twice'
        else:
            num_spottings = '%s times' % num_sightings
        place['num_spottings'] = num_spottings
        place['timesince'] = humanize_timesince(
            place['most_recent_trip'].start or place['most_recent_added_at']
        )
        if place['species'].common_name[0].lower() in 'aeiou':
            place['a_or_an'] = 'an'
        else:
            place['a_or_an'] = 'a'
        
        # Add &nbsp;s to ensure no wrapping in wrong place
        place['num_spottings'] = mark_safe(
            place['num_spottings'].replace(' ', '&nbsp;')
        )
        place['timesince'] = mark_safe(
            place['timesince'].replace(' ', '&nbsp;')
        )
    
    return render('gimmicks/index.html', {
        'gimmick': gimmick,
        'results': results,
        'name': name,
        'request_path': request.path,
        'latitude': lat,
        'longitude': lon,
    })

def humanize_timesince(start_time):
    """
    From http://www.joeyb.org/blog/2009/10/08/
        custom-django-template-filter-for-humanized-timesince
    
    Using this instead of Django's timesince filter since timesince includes
    hours and seconds, which looks a bit weird.
    """
    if isinstance(start_time, datetime.date):
        start_time = datetime.datetime(
            start_time.year, start_time.month, start_time.day
        )
    
    delta = datetime.datetime.now() - start_time

    plural = lambda x: 's' if x != 1 else ''

    num_years = delta.days / 365
    if (num_years > 0):
        return "%d year%s" % (num_years, plural(num_years))

    num_weeks = delta.days / 7
    if (num_weeks > 0):
        return "%d week%s" % (num_weeks, plural(num_weeks))

    if (delta.days > 0):
        return "%d day%s" % (delta.days, plural(delta.days))

    num_hours = delta.seconds / 3600
    if (num_hours > 0):
        return "%d hour%s" % (num_hours, plural(num_hours))

    num_minutes = delta.seconds / 60
    if (num_minutes > 0):
        return "%d minute%s" % (num_minutes, plural(num_minutes))

    return "a few seconds"