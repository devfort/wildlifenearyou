from zoo.shortcuts import render
from django.db.models import Count

from django.contrib.auth.models import User
from trips.models import Trip, Sighting
from photos.models import Photo, SuggestedSpecies
from places.models import Place
from animals.models import Species
from flickr.models import FlickrTagsApplied

import datetime

def index(request):
    return render(request, 'stats/index.html', {
        'num_users': User.objects.count(),
        'num_users_with_photos': User.objects.annotate(
            num_photos = Count('photos')
        ).filter(
            num_photos__gt = 0
        ).count(),
        'num_users_with_trips': User.objects.annotate(
            num_trips = Count('created_trip_set')
        ).filter(
            num_trips__gt = 0
        ).count(),
        'num_trips': Trip.objects.count(),
        'num_trips_with_photos': Trip.objects.filter(
            photos__isnull = True
        ).distinct().count(),
        'num_trips_without_photos': Trip.objects.filter(
            photos__isnull = False
        ).distinct().count(),
        'num_species': Species.objects.count(),
        'num_photos': Photo.objects.count(),
        'num_photos_in_past_48_hours': Photo.objects.filter(
            created_at__gte = (
                datetime.datetime.now() - datetime.timedelta(days = 2)
            )
        ).count(),
        'num_distinct_photos_tagged': FlickrTagsApplied.objects.exclude(
            tags_added = ''
        ).values('photo').distinct().count(),
        'num_distinct_photos_geotagged': FlickrTagsApplied.objects.exclude(
            latitude_added = None
        ).values('photo').distinct().count(),
        'num_distinct_photos_tagged_last_48_hours': 
            FlickrTagsApplied.objects.filter(
                created_at__gte = (
                    datetime.datetime.now() - datetime.timedelta(days = 2)
                )
            ).exclude(
                tags_added = ''
            ).values('photo').distinct().count(),
        'num_distinct_photos_geotagged_last_48_hours':
            FlickrTagsApplied.objects.filter(
                created_at__gte = (
                    datetime.datetime.now() - datetime.timedelta(days = 2)
                )
            ).exclude(
                latitude_added = None
            ).values('photo').distinct().count(),
        'num_suggestions': SuggestedSpecies.objects.count(),
        'num_suggestions_in_past_48_hours': SuggestedSpecies.objects.filter(
            suggested_at__gte = (
                datetime.datetime.now() - datetime.timedelta(days = 2)
            )
        ).count(),
        'num_suggestions_new': SuggestedSpecies.objects.filter(
            status = 'new'
        ).count(),
        'num_suggestions_rejected': SuggestedSpecies.objects.filter(
            status = 'rejected'
        ).count(),
        'num_suggestions_approved': SuggestedSpecies.objects.filter(
            status = 'approved'
        ).count(),
        'num_places': Place.objects.count(),
        'num_sightings': Sighting.objects.count(),
        'new_users_last_48_hours': User.objects.filter(
            date_joined__gte = (
                datetime.datetime.now() - datetime.timedelta(days = 2)
            )
        ),
        'new_trips_last_48_hours': Trip.objects.filter(
            created_at__gte = (
                datetime.datetime.now() - datetime.timedelta(days = 2)
            )
        )
    })
