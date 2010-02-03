from client import Flickr
from flickrapi import FlickrError
from photos.models import Photo
from django.db.models import Q

def get_photos_needing_tagging():
    return Photo.objects.filter(
        flickr_needs_tagging = True
    ).filter(
        Q(created_by__profile__flickr_tag_common_names = True) |
        Q(created_by__profile__flickr_tag_scientific_names = True)
    ).exclude(
        trip = None
    )

def get_photos_needing_geotagging():
    return Photo.objects.filter(
        flickr_needs_geotagging = True,
    ).filter(
        created_by__profile__flickr_geotag = True
    ).exclude(
        trip = None
    )

def update_flickr_location_for_photo(photo):
    profile = photo.created_by.get_profile()
    if not profile.flickr_token:
        return
    client = Flickr(token = profile.flickr_token)
    client.cache = None
    
    info = client.photos_getInfo(photo_id = photo.flickr_id)
    if 'location' in info:
        photo.flickr_needs_geotagging = False
        photo.save()
        return
    
    client.photos_geo_setLocation(
        photo_id = photo.flickr_id,
        lat = photo.trip.place.latitude,
        lon = photo.trip.place.longitude,
        accuracy = 15 # one above 16, which is street-level
        # TODO: use zoom level for place map, once we start saving that
    )
    client.photos_addTags(
        photo_id = photo.flickr_id,
        tags = 'wlny:geotagged=1'
    )
    photo.flickr_needs_geotagging = False
    photo.save()

def update_flickr_tags_for_photo(photo):
    profile = photo.created_by.get_profile()
    if not profile.flickr_token:
        return
    client = Flickr(token = profile.flickr_token)
    client.cache = None
    
    info = client.photos_getInfo(photo_id = photo.flickr_id)
    existing_tags = [t['raw'] for t in info['photo']['tags']['tag']]
    
    desired_tags = []
    for sighting in photo.sightings.all():
        if sighting.species:
            desired_tags.append('wlny:species=%s' % sighting.species.pk)
            if profile.flickr_tag_common_names:
                desired_tags.append(sighting.species.common_name)
            if profile.flickr_tag_scientific_names and \
                    sighting.species.latin_name:
                desired_tags.append(sighting.species.latin_name)
        elif sighting.species_inexact:
            desired_tags.append(sighing.s.species_inexact)
    
    tags_to_add = [t for t in desired_tags if t not in existing_tags]
    
    # And the machine tags...
    tags_to_add.append('wlny:tagged=1')
    tags_to_add.append('wlny:photo=%s' % photo.pk)
    if photo.trip:
        tags_to_add.append('wlny:trip=%s' % photo.trip.pk)
        tags_to_add.append('wlny:place=%s' % photo.trip.place.pk)
    
    new_tags = ' '.join(['"%s"' % t for t in tags_to_add])
    
    client.photos_addTags(photo_id = photo.flickr_id, tags = new_tags)
    photo.flickr_needs_tagging = False
    photo.save()
