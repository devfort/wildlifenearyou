from django.shortcuts import get_object_or_404, render_to_response as render
from models import Gimmick
from places.models import Place
from animals.models import Species

from zoo.search.geocoders import google_geocode
import geopy, geopy.distance

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
        return gimmick_results(request, gimmick, '', lat, lon)
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
    
    results = all_possible_places[:3]
    
    # Now load the actual ORM objects
    place_pks = set([p['pk'] for p in results])
    places = Place.objects.in_bulk(list(place_pks))
    species_pks = set([p['animals_species_id'] for p in results])
    species = Species.objects.in_bulk(list(species_pks))
    
    for place in results:
        place['place'] = places[place['pk']]
        place['species'] = species[place['animals_species_id']]
        photo = place['place'].photo_of(place['species'])
        place['photo'] = photo or place['species'].photo()
    
    return render('gimmicks/index.html', {
        'gimmick': gimmick,
        'results': results,
        'name': name,
        'request_path': request.path,
    })
