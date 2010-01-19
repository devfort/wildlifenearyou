from zoo.accounts.models import Profile
from zoo.places.models import Place
from zoo.trips.models import Trip
from django.db.models import Count
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import simplejson

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
