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
    ).exclude(
        created_by__profile__flickr_token = ''
    )

def get_photos_needing_geotagging():
    return Photo.objects.filter(
        flickr_needs_geotagging = True,
    ).filter(
        created_by__profile__flickr_geotag = True
    ).exclude(
        trip = None
    ).exclude(
        created_by__profile__flickr_token = ''
    )

def update_flickr_location_for_photo(photo):
    profile = photo.created_by.get_profile()
    if not profile.flickr_token:
        return
    client = Flickr(token = profile.flickr_token)
    client.cache = None
    
    try:
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
        photo.flickr_tags_applied.create(
            latitude_added = photo.trip.place.latitude,
            longitude_added = photo.trip.place.longitude,
        )
        photo.flickr_needs_geotagging = False
        photo.save()
    except FlickrError, e:
        # We assume it's a token problem, so clear their token
        profile.flickr_token = ''
        profile.save()

def short(obj):
    return obj.short_url().split('/')[-1]

def update_flickr_tags_for_photo(photo):
    profile = photo.created_by.get_profile()
    if not profile.flickr_token:
        return
    client = Flickr(token = profile.flickr_token)
    client.cache = None
    
    try:
        info = client.photos_getInfo(photo_id = photo.flickr_id)
        existing_tags = [t['raw'] for t in info['photo']['tags']['tag']]
        
        machine_tags = ['wlny:photo=%s' % short(photo)]
        desired_tags = []
        for sighting in photo.sightings.all():
            if sighting.species:
                machine_tags.append(
                    'wlny:species=%s' % short(sighting.species)
                )
                if profile.flickr_tag_common_names:
                    desired_tags.append(sighting.species.common_name)
                if profile.flickr_tag_scientific_names and \
                        sighting.species.latin_name:
                    desired_tags.append(sighting.species.latin_name)
            elif sighting.species_inexact:
                desired_tags.append(sighting.species_inexact)
        
        regular_tags_to_add = [
            t for t in desired_tags if t not in existing_tags
        ]
        
        if photo.trip:
            machine_tags.append('wlny:trip=%s' % short(photo.trip))
            machine_tags.append('wlny:place=%s' % short(photo.trip.place))
        
        new_tags = u' '.join([
            u'"%s"' % t for t in (regular_tags_to_add + machine_tags)
        ])
        
        client.photos_addTags(photo_id = photo.flickr_id, tags = new_tags)
        
        regular_tags_added = u' '.join([
            u'"%s"' % t for t in regular_tags_to_add
        ])
        if regular_tags_added:
            photo.flickr_tags_applied.create(
                tags_added = regular_tags_added
            )
        photo.flickr_needs_tagging = False
        photo.save()
    except FlickrError, e:
        # We assume it's a token problem, so clear their token
        profile.flickr_token = ''
        profile.save()
