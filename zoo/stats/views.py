from zoo.shortcuts import render
from django.db.models import Count

from django.contrib.auth.models import User
from trips.models import Trip, Sighting
from photos.models import Photo
from places.models import Place
from animals.models import Species

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
        'num_species': Species.objects.count(),
        'num_photos': Photo.objects.count(),
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
