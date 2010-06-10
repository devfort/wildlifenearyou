from zoo.accounts.models import Profile
from zoo.places.models import Place
from zoo.trips.models import Trip
from zoo.linkeddata.models import ExternalIdentifier
from zoo.animals.models import Species
from zoo.shortcuts import render
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.shortcuts import get_object_or_404
from zoo.shorturl.utils import converter
from utils import api_response, api_date, api_datetime
from ratelimit import ratelimit
from models import ApiKey, ApiKeyGroup

MAX_METADATA = 20

import urllib
from collections import defaultdict

def index(request):
    return render(request, 'api/index.html')

@login_required
def your_keys(request):
    if request.method == 'POST':
        if 'create_key' in request.POST:
            purpose = request.POST.get('purpose', '')
            group, created = ApiKeyGroup.objects.get_or_create(
                name = 'default'
            )
            key = ApiKey.create_for_user(request.user, group, purpose)
            return HttpResponseRedirect('/api/your-keys/')
        
        # Are they deleting a key?
        for k in request.POST.keys():
            if k.startswith('delete_'):
                key = k.replace('delete_', '')
                try:
                    api_key = ApiKey.objects.get(
                        key = key,
                        user = request.user
                    )
                    api_key.delete()
                except ApiKey.DoesNotExist:
                    pass
                return HttpResponseRedirect('/api/your-keys/')
    
    return render(request, 'api/your_keys.html', {
        'keys': request.user.api_keys.select_related('group').order_by(
            'created_at'
        ),
    })

@login_required
def key_details(request, key):
    api_key = get_object_or_404(ApiKey.objects.select_related('group'),
        key = key,
        user = request.user
    )
    return render(request, 'api/key_details.html', {
        'key': api_key,
    })

trip_qs = Trip.objects.select_related('place').annotate(
    num_sightings = Count('sightings')
).values(
    'pk', 'created_at', 'place__known_as', 'start', 'start_accuracy', 'name',
    'place__pk', 'place__country__country_code', 'num_sightings',
    'place__slug'
)

@ratelimit
def user(request, username):
    try:
        profile = Profile.objects.annotate(
            num_trips = Count('user__created_trip_set')
        ).select_related('user').get(user__username = username)
    except Profile.DoesNotExist:
        return api_response(request, 404, {
            'username': username
        }, ok = False)
    
    info = {
        'username': username,
        'first_name': profile.user.first_name,
        'last_name': profile.user.first_name,
        'url': profile.url,
        'biography': profile.biography,
        'num_trips': profile.num_trips,
        'trips_api': 'http://www.wildlifenearyou.com/api/%s/trips/' % (
             username
        ),
        'species_seen_api': 'http://www.wildlifenearyou.com/api/%s/species/'%(
             username
        ),
    }
    return api_response(request, 200, info)

@ratelimit
def user_trips(request, username):
    try:
        user = User.objects.get(username = username)
    except User.DoesNotExist:
        return api_response(request, 404, {
            'username': username
        }, ok = False)
    return api_response(request, 200, {
        'username': username,
        'trips': [{
            'api_url': 'http://www.wildlifenearyou.com/api/%s/trips/%s/' % (
                username, trip['pk']
            ),
            'url': 'http://www.wildlifenearyou.com/%s/trips/%s/' % (
                username, trip['pk']
            ),
            'name': trip['name'],
            'code': 't' + converter.from_int(trip['pk']),
            'short_url': 'http://wlny.eu/t' + converter.from_int(trip['pk']),
            'date': api_date(trip['start']),
            'date_accuracy': trip['start_accuracy'],    
            'created': api_datetime(trip['created_at']),
            'num_sightings': trip['num_sightings'],
            'place': {
                'known_as': trip['place__known_as'],
                'api_url': 'http://www.wildlifenearyou.com/api/%s/%s/' % (
                    trip['place__country__country_code'], trip['place__slug']
                ),
                'code': 'p' + converter.from_int(trip['place__pk']),
                'short_url': 'http://wlny.eu/p' + \
                    converter.from_int(trip['place__pk']),
                'url': 'http://www.wildlifenearyou.com/%s/%s/' % (
                     trip['place__country__country_code'], trip['place__slug']
                )
            },
        } for trip in trip_qs.filter(created_by = user)]
    })

@ratelimit
def user_species(request, username):
    try:
        user = User.objects.get(username = username)
    except User.DoesNotExist:
        return api_response(request, 404, {
            'username': username
        }, ok = False)
    species_seen = Species.objects.filter(
        sightings__created_by = user
    ).annotate(
        times_seen = Count('sightings')
    ).values('common_name', 'latin_name', 'slug', 'times_seen', 'pk')
    return api_response(request, 200, {
        'username': username,
        'species': [{
            'api_url': 'http://www.wildlifenearyou.com/api/species/%s/' % (
                species['slug']
            ),
            'common_name': species['common_name'],
            'latin_name': species['latin_name'],
            'code': 's' + converter.from_int(species['pk']),
            'short_url': 'http://wlny.eu/s'+converter.from_int(species['pk']),
            'times_seen': species['times_seen'],
        } for species in species_seen]
    })

@ratelimit
def trip(request, username, pk):
    try:
        trip = Trip.objects.get(pk = pk, created_by__username = username)
    except Trip.DoesNotExist:
        return api_response(request, 404, {
            'username': username,
            'trip_id': pk,
        }, ok = False)
    return api_response(request, 200, {
        'name': trip.name,
        'todo': 'finish me',
    })

@ratelimit
def place(request, country_code, slug):
    pass

@ratelimit
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
            'external_identifiers': [{
                'source': d['source'],
                'namespace': d['namespace'],
                'key': d['key'],
                'uri': d['uri'],
            } for d in species_identifiers.get(s.pk, [])]
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

@ratelimit
def metadata(request, ids):
    ids = ids.replace('/', '')
    ids = [id.strip() for id in ids.split(',') if id.strip()]
    
    if len(set(ids)) > MAX_METADATA:
        return api_response(request, 500, {
            'ok': False,
            'reason': 'Max %s ids allowed' % MAX_METADATA
        })
    
    results = dict(zip(ids, [{'ok': False} for id in ids]))
    
    from shorturl.views import PREFIXES
    to_process = {}
    for shortcode in ids:
        if shortcode[0] in PREFIXES:
            try:
                pk = converter.to_int(shortcode[1:])
            except ValueError:
                continue
            to_process.setdefault(
                PREFIXES[shortcode[0]], {}
            )[pk] = shortcode
    
    for model, codes in to_process.items():
        pks = codes.keys()
        found = model.objects.in_bulk(pks)
        for pk, obj in found.items():
            results[codes[pk]] = {
                'ok': True,
                'shortcode': codes[pk],
                'shorturl': 'http://wlny.eu/%s' % codes[pk],
                'title': str(obj),
                'url': 'http://www.wildlifenearyou.com%s' % \
                    obj.get_absolute_url(),
                'type': model._meta.verbose_name,
            }
    
    return api_response(request, 200, {'results': results, 'ok': True})
