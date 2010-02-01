from django.http import HttpResponse, HttpResponseRedirect, Http404, \
    HttpResponseServerError
from zoo.shortcuts import render
from django.conf import settings

from zoo.places.models import Place, Country
from zoo.accounts.forms import RegistrationForm
from zoo.animals.models import Species
from zoo.trips.models import Sighting, Trip
from zoo.accounts.models import Profile
from zoo.photos.models import Photo
from zoo.favourites.models import FavouritePhoto
from zoo.utils import location_from_request

from basic.blog.models import Post

import itertools

def homepage(request):

    reg_form = RegistrationForm()

    recent_sightings = Sighting.objects.order_by('-created_at')
    recent_sightings_favourites = None
    if request.user.is_authenticated():
        favourite_animals = Species.objects.filter(favourited=request.user)
        recent_sightings_favourites = Sighting.objects.filter(
            species__in=favourite_animals
        ).order_by('-created_at')

    featured = {}

    # Doing it this way means the page survives with 0 or >1 featured
    # sites.
    places = Place.objects.filter(featured=True).order_by('?')
    featured['place'] = places.count() > 0 and places[0] or None

    species = Species.objects.filter(featured=True).order_by('?')
    featured['species'] = species.count() > 0 and species[0] or None

    profiles = Profile.objects.filter(featured=True).order_by('?')
    featured['profile'] = profiles.count() > 0 and profiles[0] or None

    num_of_places = Place.objects.count()
    num_of_countries = Country.objects.filter(
        place__isnull = False
    ).distinct().count()

    if featured['place']:
        # Have to do this as django template method calls can't take params.
        try:
            featured['place'].species = featured['place'].get_species(
                limit=10
            )
        except Species.DoesNotExist:
            featured['place'].species = None

    if featured['species']:
        location, (lat, lon) = location_from_request(request)
        if (lat, lon) != (None, None):
            from zoo.search import nearest_places_with_species as npws
            nearest_species = npws(
                featured['species'].common_name, (lat, lon)
            )
            if nearest_species:
                featured['species'].nearest = nearest_species[0]
    
    if settings.SEARCH_ENABLED:
        default_search = ''
    else:
        default_search = 'SEARCH CURRENTLY DISABLED'
    
    return render(request, 'homepage.html', {
        'featured': featured,
        'num_of_places': num_of_places,
        'num_of_countries': num_of_countries,
        'reg_form': reg_form,
        'recent_sightings': recent_sightings,
        'recent_sightings_favourites': recent_sightings_favourites,
        'default_search': default_search,
        'recent_photos': recent_photos_for_homepage(),
        'recent_trips': recent_trips_for_homepage(5),
        'blog_posts': Post.objects.published(),
#        'recent_trips': Trip.objects.filter(
#            start__isnull=False
#        ).order_by('-start')[:5]
    })

def recent_photos_for_homepage():
    faves = FavouritePhoto.objects.order_by(
        '-when_added'
    ).select_related('photo').filter(photo__is_visible=True)[:20]
    pks = [f.photo_id for f in faves]
    recents = Photo.objects.select_related('created_by').filter(
        is_visible = True
    ).exclude(pk__in = pks).order_by('-created_at')[:20]
    
    seen_user_ids = set()
    seen_photo_ids = set()
    photos = []
    skipped_photos = []
    
    iter_faves = itertools.cycle(f.photo for f in faves)
    iter_recents = itertools.cycle(recents)
    
    while len(photos) < 20:
        while True:
            try:
                next = iter_recents.next()
            except StopIteration:
                break
            if next.pk in seen_photo_ids:
                continue
            photos.append(next)
            seen_photo_ids.add(next.pk)
            break
        
        while True:
            try:
                next = iter_faves.next()
            except StopIteration:
                break
            if next.pk in seen_photo_ids:
                continue
            photos.append(next)
            seen_photo_ids.add(next.pk)
            break
    
    return photos

def recent_trips_for_homepage(count = 5):
    # Return recent trips, but only a maximum of one per user (unless all 
    # 20 of the most recent trips are by the same person)
    seen_user_ids = set()
    trip_ids = []
    skipped_trip_ids = []
    for trip_id, user_id in Trip.objects.order_by('-created_at').values_list(
            'pk', 'created_by'
        )[:count * 4]:
        if user_id in seen_user_ids:
            skipped_trip_ids.append(trip_id)
        else:
            seen_user_ids.add(user_id)
            trip_ids.append(trip_id)
    # Backfill with skipped trips, if required
    trip_ids = trip_ids[:count]
    for i in range(len(trip_ids) - count):
        trip_ids.append(skipped_trip_ids[i])
    return Trip.objects.filter(pk__in = trip_ids).order_by('-created_at')
