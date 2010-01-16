from django import forms
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden

from zoo.shortcuts import render
from zoo.photos.models import Photo
from zoo.trips.models import Trip
from models import FlickrSet
from client import Flickr

import datetime
from dateutil import parser

from django_openid import signed

def flickr_redirect(path):
    # Send them off to Flickr to authenticate, but first 
    # we need to set a cookie specifying where they should come BACK to 
    # since Flickr will return them to /flickr/callback/
    response = HttpResponseRedirect(Flickr().web_login_url("write"))
    response.set_cookie('flickr_return_to', path)
    return response

def flickr_callback(request):
    return_to = request.COOKIES.get('flickr_return_to', '/')
    flickr_token = Flickr().get_token(request.GET.get('frob', ''))
    response = HttpResponseRedirect(return_to)
    response.set_cookie('flickr_token', flickr_token)
    response.delete_cookie('flickr_return_to')
    return response

@login_required
def index(request):
    flickr_token = request.COOKIES.get('flickr_token')
    if not flickr_token:
        return flickr_redirect(request.path)
    page = request.GET.get('page', '1')
    try:
        page = max(int(page), 1)
    except ValueError:
        page = 1
    client = Flickr(token = flickr_token)
    token_info = client.auth_checkToken()
    user_id = token_info['auth']['user']['nsid']
    result = client.photos_search(
        user_id = 'me', per_page = 24, page = page,
        extras = 'date_taken'
    )
    photos = result['photos']['photo']
    num_pages = result['photos']['pages']
    return photo_picker(
        request, photos, 'Your recent photos', {
            'paginated': num_pages > 1,
            'num_pages': num_pages,
            'page': page,
            'has_next': page < num_pages,
            'next_page': page + 1,
            'has_prev': page > 1,
            'prev_page': page - 1,
        }
    )

@login_required
def places(request):
    flickr_token = request.COOKIES.get('flickr_token')
    if not flickr_token:
        return flickr_redirect(request.path)
    client = Flickr(token = flickr_token)
    token_info = client.auth_checkToken()
    user_id = token_info['auth']['user']['nsid']
    return render(request, 'flickr/places.html', {
        'places': client.places_placesForUser(
            place_type = 'locality',
        ),
    })

@login_required
def groups(request):
    flickr_token = request.COOKIES.get('flickr_token')
    if not flickr_token:
        return flickr_redirect(request.path)
    client = Flickr(token = flickr_token)
    token_info = client.auth_checkToken()
    user_id = token_info['auth']['user']['nsid']
    return render(request, 'flickr/groups.html', {
        'groups': client.people_getPublicGroups(user_id = user_id),
    })

@login_required
def group(request, group_nsid):
    flickr_token = request.COOKIES.get('flickr_token')
    if not flickr_token:
        return flickr_redirect(request.path)
    client = Flickr(token = flickr_token)
    token_info = client.auth_checkToken()
    group_info = client.groups_getInfo(group_id = group_nsid)
    user_id = token_info['auth']['user']['nsid']
    photos = client.groups_pools_getPhotos(
        group_id = group_nsid, user_id = user_id, extras = 'date_taken'
    )['photos']['photo']
    return photo_picker(
        request, photos, 'Your photos in %s' % group_info['group']['name']
    )

@login_required
def sets(request):
    flickr_token = request.COOKIES.get('flickr_token')
    if not flickr_token:
        return flickr_redirect(request.path)
    client = Flickr(token = flickr_token)
    sets = client.photosets_getList()['photosets']['photoset']
    return render(request, 'flickr/sets.html', {
        'sets': sets,
        'show_photos': len(sets) <= 30,
    })

@login_required
def single_set(request, set_id):
    flickr_token = request.COOKIES.get('flickr_token')
    if not flickr_token:
        return flickr_redirect(request.path)
    client = Flickr(token = flickr_token)
    token_info = client.auth_checkToken()
    user_id = token_info['auth']['user']['nsid']
    photos = client.photosets_getPhotos(
        photoset_id = set_id, media = 'photos', extras = 'date_taken'
    )['photoset']['photo']
    set_info = client.photosets_getInfo(
        photoset_id = set_id
    )['photoset']
    set_details = {
        'set_title': set_info['title'],
        'set_id': set_info['id'],
        'set_description': set_info['description'],
    }
    return photo_picker(
        request, photos, 'Your set: %s' % set_details['set_title'],
        set_details = set_details
    )

@login_required
def place(request, woe_id):
    flickr_token = request.COOKIES.get('flickr_token')
    if not flickr_token:
        return flickr_redirect(request.path)
    client = Flickr(token = flickr_token)
    token_info = client.auth_checkToken()
    user_id = token_info['auth']['user']['nsid']
    place_info = client.places_getInfo(woe_id = woe_id)
    photos = client.photos_search(
        woe_id = woe_id, user_id = user_id, extras = 'date_taken'
    )['photos']['photo']
    return photo_picker(
        request, photos, 'Your photos in %s' % place_info['place']['name']
    )

def photo_picker(request, photos, title, extra_context=None,set_details=None):
    # Enhance each photo with a signed dict for the checkbox field, so if 
    # they DO select that photo we won't have to do another API call to look 
    # up its details on Flickr
    photo_ids = [photo['id'] for photo in photos]
    already_imported_ids = set(Photo.objects.filter(
        flickr_id__in = photo_ids
    ).values_list('flickr_id', flat=True))
    enable_button = False
    for photo in photos:
        photo_info = {
            'id': photo['photo_id'],
            'farm': photo['farm'],
            'secret': photo['secret'],
            'server': photo['server'],
            'title': photo['title'],
            'taken_at': photo['datetaken'],
        }
        if set_details:
            photo_info.update(set_details)
        photo['signed'] = signed.dumps(photo_info)
        already_imported = photo['photo_id'] in already_imported_ids
        photo['already_imported'] = already_imported
        if not already_imported:
            enable_button = True
    
    context = {
        'title': title,
        'photos': photos,
        'enable_button': enable_button,
    }
    if extra_context is not None:
        context.update(extra_context)
    
    return render(request, 'flickr/photo_picker.html', context)

@login_required
def search(request):
    "Search your own photos"
    q = request.GET.get('q', '')
    if not q:
        return render(request, 'flickr/search.html')
    
    flickr_token = request.COOKIES.get('flickr_token')
    if not flickr_token:
        return flickr_redirect(request.path)
    client = Flickr(token = flickr_token)
    token_info = client.auth_checkToken()
    user_id = token_info['auth']['user']['nsid']
    photos = client.photos_search(
        user_id = user_id,
        text = q,
        extras = 'date_taken'
    )['photos']['photo']
    return photo_picker(request, photos, 'Search for "%s"' % q)

def flickr_error(request, msg):
    return render(request, 'flickr/error.html', {
        'msg': msg,
    })

@login_required
def selected(request):
    "Should only ever be POSTed to with a list of photo IDs in the 'photo'"
    photos_to_add = []
    for photo in request.POST.getlist('photo'):
        try:
            photos_to_add.append(signed.loads(photo))
        except ValueError:
            continue # Skip any that don't pass the signature check
    # Moderation is currently disabled:
    # is_visible = (
    #     request.user.get_profile().is_not_brand_new_account() or \
    #     request.user.is_staff
    # )
    is_visible = True
    added_ids = []
    set_id = None
    for photo in photos_to_add:
        if Photo.objects.filter(flickr_id = photo['id']).count():
            continue
        p = Photo.objects.create(
            created_by = request.user,
            created_at = datetime.datetime.now(),
            title = photo['title'],
            photo = '',
            flickr_id = photo['id'],
            flickr_secret = photo['secret'],
            flickr_server = photo['server'],
            is_visible = is_visible,
            taken_at = parser.parse(photo['taken_at']),
        )
        added_ids.append(p.id)
        # Should we add it to a set as well?
        if 'set_id' in photo:
            flickr_set, created = FlickrSet.objects.get_or_create(
                flickr_id = photo['set_id'],
                defaults = {
                    'title': photo['set_title'],
                    'description': photo['set_description'],
                    'user': request.user,
                }
            )
            flickr_set.photos.add(p)
            set_id = photo['set_id']
    
    url = '/%s/photos/unassigned/' % request.user.username
    if set_id:
        url = '/%s/photos/unassigned/by-flickr-set/%s/' % (
            request.user.username,
            set_id
        )
    
    if added_ids:
        url += '?ids=' + (','.join(map(str, added_ids)))
    
    return HttpResponseRedirect(url)
