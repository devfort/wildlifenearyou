from zoo.accounts.models import Profile
from zoo.places.models import Place
from zoo.trips.models import Trip
from zoo.linkeddata.models import ExternalIdentifier
from zoo.animals.models import Species
from django.db.models import Count
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import simplejson
from zoo.shorturl.utils import converter

import urllib
from collections import defaultdict

trip_qs = Trip.objects.select_related('place').annotate(
    num_sightings = Count('sightings')
).values(
    'pk', 'created_at', 'place__known_as', 'start', 'start_accuracy', 'name',
    'place__pk', 'place__country__country_code', 'num_sightings',
    'place__slug'
)

def user(request, username):
    try:
        profile = Profile.objects.annotate(
            num_trips = Count('user__created_trip_set')
        ).select_related('user').get(user__username = username)
    except Profile.DoesNotExist:
        return api_response(request, 404, {
            'ok': False,
            'username': username
        })
    
    info = {
        'ok': True,
        'username': username,
        'first_name': profile.user.first_name,
        'last_name': profile.user.first_name,
        'url': profile.url,
        'biography': profile.biography,
        'num_trips': profile.num_trips,
        'trips_api': 'http://www.wildlifenearyou.com/api/%s/tripbook/' % (
             username
        )
    }
    return api_response(request, 200, info)

def tripbook(request, username):
    try:
        user = User.objects.get(username = username)
    except User.DoesNotExist:
        return api_response(request, 404, {
            'ok': False,
            'username': username
        })
    return api_response(request, 200, {
        'ok': True,
        'username': username,
        'trips': [{
            'api_url': 'http://www.wildlifenearyou.com/api/%s/trips/%s/' % (
                username, trip['pk']
            ),
            'name': trip['name'],
            'date': api_date(trip['start']),
            'date_accuracy': trip['start_accuracy'],    
            'created': api_datetime(trip['created_at']),
            'num_sightings': trip['num_sightings'],
            'place_known_as': trip['place__known_as'],
            'place_api': 'http://www.wildlifenearyou.com/api/%s/%s/' % (
                trip['place__country__country_code'], trip['place__slug']
            )
        } for trip in trip_qs.filter(created_by = user)]
    })

def trip(request, username, pk):
    pass

def place(request, country_code, slug):
    pass

def api_response(request, status_code, info):
    info['status'] = status_code
    if request.GET.get('format', '') == 'html':
        return HttpResponse(
            '<html><head><title>API response</title></head><body><pre>' + 
            simplejson.dumps(info, indent=2) + 
            '</pre></body></html>',
            content_type='text/html; charset=utf8'
        )
    
    return HttpResponse(
        simplejson.dumps(info, indent=2),
        content_type='text/plain; charset=utf8'
    )

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

def species_identifiers(request):
    all = Species.objects.all().order_by('slug')
    allowed_args = ('namespace', 'source', 'key', 'code', 'slug', 'after')
    external_identifier_args = ('namespace', 'source', 'key')
    provided_args = [
        (arg, request.GET.get(arg, None))
        for arg in allowed_args
    ]
    for arg, value in provided_args:
        if value is None:
            continue
        if arg in external_identifier_args:
            all = all.filter(**{
                'external_identifiers__%s' % arg: value
            })
        elif arg == 'code':
            all = all.filter(pk = converter.to_int(value[1:]))
        elif arg == 'slug':
            all = all.filter(slug = value)
        elif arg == 'after': # Deal with pagination
            all = all.filter(slug__gte = value)
    
    # We only serve up 50 at a time
    all = list(all[:51])
    next_after = None
    if len(all) == 51:
        next_after = all[-1].slug
        all = all[:-1]
    
    # Now fetch the external identifiers in one big go
    identifiers = ExternalIdentifier.objects.filter(**dict([
        (k, v) for k, v in provided_args
        if k in external_identifier_args and v is not None
    ])).filter(
        species__in = [s.pk for s in all]
    ).values('species_id', 'source', 'namespace', 'key', 'uri')
    species_identifiers = defaultdict(list)
    for identifier in identifiers:
        species_identifiers[identifier['species_id']].append(identifier)
    
    species = []
    for s in all:
        species.append({
            'url': 'http://www.wildlifenearyou.com%s' % ( 
                s.get_absolute_url()
            ),
            'code': s.short_code(),
            'short_url': s.short_url(),
            'common_name': s.common_name,
            'latin_name': s.latin_name,
            'slug': s.slug,
            'external_identifiers': species_identifiers.get(s.pk) or []
        })
    
    result = {
        'ok': True,
        'species': species,
        'args': {}
    }
    
    for arg, value in provided_args:
        if value is not None:
            result['args'][arg] = value
    
    if next_after:
        result['next'] = 'http://www.wildlifenearyou.com%s?%s' % (
            request.path, urllib.urlencode(dict([
                (key, value) for key, value in provided_args if (
                    key != 'after' and value is not None
                )
            ] + [('after', next_after)]))
        )
    
    return api_response(request, 200, result)
