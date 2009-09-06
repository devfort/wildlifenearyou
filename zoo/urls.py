from django.conf.urls.defaults import *
from django.conf import settings
from django import http
from django.views.generic.simple import direct_to_template

import os

from django.contrib import admin
admin.autodiscover()

from django.contrib import databrowse
from django.contrib.auth.models import User
from django.db.models import get_models
from dmigrations.migration_state import table_present
#for model in get_models():
#    if table_present(model._meta.db_table):
#        databrowse.site.register(model)

from django.template import add_to_builtins
add_to_builtins('zoo.common.templatetags.switch')

from accounts import views as accounts
from faces import views as faces
from photos import views as photos

from accounts.openid import RegistrationConsumer
#from invitereg.views import InviteRegistrationConsumer as RegistrationConsumer

registration_consumer = RegistrationConsumer()

urlpatterns = patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': os.path.join(settings.OUR_ROOT, 'static')
    }),
    
    # Invitation URL (sent out in invite e-mail)
    url(r'^invitation/$', 'zoo.invitereg.views.enter_invite_code',
        name = 'enter-invite-code'
    ),
    url(r'^invitation/clear/$', 'zoo.invitereg.views.clear_invite_code',
        name = 'clear-invite-code'
    ),
    (r'^invitation/(\w+)/$', 'zoo.invitereg.views.invitation'),
    
    url(r'^account/register/$', registration_consumer, {
        'rest_of_url': 'register/',
    }, name = 'accounts-register'),
    url(r'^account/login/$', registration_consumer, {
        'rest_of_url': 'login/',
    }, name = 'accounts-login'),
    url(r'^account/logout/$', registration_consumer, {
        'rest_of_url': 'logout/',
    }, name = 'accounts-logout'),
    (r'^account/(.*?)$', registration_consumer),
    
    (r'^blog/', include('basic.blog.urls')),
    
    # Landing Page
    url(r'^$', 'zoo.homepage.views.homepage',
        name='homepage'
    ),
    
    url(r'^debug/urls/$', 'zoo.debug.views.show_url_patterns'),
    
    # Launch signups POST handler
    (r'^launchsignups/$', 'zoo.launchsignups.views.signup'),
    
    # shortcuts
    url(r'^tripbook/$', 'zoo.trips.views.tripbook_default',
        name='tripbook-default'),
    url(r'^profile/$', accounts.profile_default,
        name='accounts-default'),
    url(r'^invite/$', accounts.invite_friends,
        name='invite-friends'),
    
    url(r'^search/species/$', 'zoo.search.views.search_species', 
        name='species-search'),
    url(r'^search/$', 'zoo.search.views.search',
        name='search'),
    
    # Ajax autocompleters
    url(r'^autocomplete/species/(\d+)/$', 
        'zoo.trips.views.autocomplete_species',
        name='autocomplete-species-place'),

    # Flickr integration
    url(r'^flickr/$', 'zoo.flickr.views.index',
        name='flickr'),
    url(r'^flickr/callback/$', 'zoo.flickr.views.flickr_callback',
        name='flickr-callback'),
    url(r'^flickr/search/$', 'zoo.flickr.views.search',
        name='flickr-search'),
    url(r'^flickr/your-places/$', 'zoo.flickr.views.places',
        name='flickr-places'),
    url(r'^flickr/your-places/(.*?)/$', 'zoo.flickr.views.place',
        name='flickr-place'),
    url(r'^flickr/your-groups/$', 'zoo.flickr.views.groups',
        name='flickr-groups'),
    url(r'^flickr/your-groups/(.*?)/$', 'zoo.flickr.views.group',
        name='flickr-group'),
    url(r'^flickr/your-sets/$', 'zoo.flickr.views.sets',
        name='flickr-sets'),
    url(r'^flickr/your-sets/(.*?)/$', 'zoo.flickr.views.single_set',
        name='flickr-set'),
    url(r'^flickr/selected/$', 'zoo.flickr.views.selected',
        name='flickr-selected'),
    
    url(r'^forgotten_password/$', 'accounts.views.forgotten_password',
        name='forgotten-password'),
    url(r'^password_key_sent/$', 'accounts.views.password_key_sent',
        name='password-key-sent'),
    url(r'^recover_password/(\w+)/([a-f0-9]+)/([a-f0-9]{32})/$', 
        'accounts.views.recover_password',
        name='recover-password'),
    url(r'^change_password/$', 'django.contrib.auth.views.password_change', {
            'template_name': 'accounts/change_password.html'
        }, name='change-password'),
    url(r'^change_password_done/$', 
        'django.contrib.auth.views.password_change_done', {
            'template_name': 'accounts/change_password_done.html'
        }, name='change-password-done'),
    
    url(r'^register/validate/(\w+)/([a-f0-9]+)/([a-f0-9]{32})/$', 
        'accounts.views.validate_email',
        name='validate-email'),
    url(r'^register/validated/$', 'accounts.views.validate_email_success',
        name='validate-email-success'),
    
    url(r'^profiles/$', accounts.all_profiles,
        name='accounts-all-profiles'),
    
    url(r'^add-trip/$', 'trips.views.add_trip_select_place', name='add-trip'),
    url(r'^add-trip/add-place/$', 'trips.views.add_trip_add_place', 
        name='add-trip-add-place'),
    
    (r'^faces/profile-images.xml$', faces.profile_images_xml),
    (r'^faces/profile.xml$', faces.profile_xml),
    url(r'^faces/large/(?P<username>\w+).png$',
        'faces.generate.profile_image_response',
        name="profile-image",
        kwargs = {'size': 'large'}
    ),
    url(r'^faces/small/(?P<username>\w+).png$',
        'faces.generate.profile_image_response',
        name="profile-image-resized",
        kwargs = {'size': 'small'}
    ),
    url(r'^faces/medium/(?P<username>\w+).png$',
        'faces.generate.profile_image_response',
        name="profile-image-resized-medium",
        kwargs = {'size': 'medium'}
    ),
    (r'^faces/users/(\w+).xml$', faces.profile_image_xml),
    (r'^faces/update/$', faces.update),
    
    url(r'^photos/upload/$', photos.upload, name="upload-photos"),
    (r'^photos/$', photos.all),
    url(r'^moderation/photos/$', 'zoo.photos.views.moderate', 
        name='moderate-photos'),
    
    (r'^set-location/$', 'zoo.accounts.views.set_location'),
    (r'^set-location/delete/$', 'zoo.accounts.views.delete_location'),
    url(r'location-complete/$', 'zoo.search.views.location_complete',
        name="location-complete"),
    
    (r'^comments/', include('django.contrib.comments.urls')),
    url(r'^feedback/$', 'zoo.feedback.views.submit', name='feedback'),
    
    # Django built-in admin
    (r'^admin/(.*)', admin.site.root),
    
    # Databrowse
    (r'^databrowse/(.*)', databrowse.site.root),
    
    url(r'^animals/$', 'zoo.animals.views.all_species',
        name='all-species'),
    url(r'^animals/all\.xml$', 'zoo.animals.views.species_xml',
        name='species-xml'),
    url(r'^animals/(?P<slug>[^/]+)/$', 'zoo.animals.views.species',
        name='species'),
    url(r'^animals/(?P<slug>[^/]+)/spotters/$', 
        'zoo.animals.views.species_spotters',
        name='species-spotters'),
    
    url(r'^favourite/(?P<action>add|remove)/$', 
        'zoo.favourites.views.handle_favourite',
        name='favourite-species'),
    
    url(r'^latin/$', 'zoo.animals.views.all_species_latin',
        name='all-species-latin'),
    url(r'^latin/(?P<latin_name>[^/]+)/$', 
        'zoo.animals.views.species_latin',),
    
    url(r'^popular/$', 'zoo.favourites.views.hit_parade',
        name='popular'),
    
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/$', 
        'zoo.places.views.place',
        name='place'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>.*?)/suggest-changes/$',
        'zoo.places.views.place_edit', name='place-edit'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>.*?)/changes-suggested/$',
        'zoo.places.views.place_edit_done', name='place-edit-done'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>.*?)/summary/$', 
        'zoo.places.views.place_summary',
        name='place-summary'),
    
    url(r'^places/$', 'zoo.places.views.all_places',
        name='places'),
    url(r'^places/autocomplete/$', 'zoo.search.views.place_complete',
        name='places-autocomplete'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/animal-checklist/$', 
        'zoo.places.views.place_animal_checklist',
        name='place-animal-checklist'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/animals/$', 
        'zoo.places.views.place_species',
        name='place-species'),
    url(r'^(?P<country>\w{2})/(?P<place>[^/]+)/animals/(?P<species>[^/]+)/$',
        'zoo.places.views.place_species_view',
        name='place-species-view'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/add-trip/$',
        'zoo.trips.add_trip.add_trip',
        name='place-add-trip'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/add-trip/ajax-search/$',
        'zoo.trips.add_trip.ajax_search_species',
        name='place-add-trip-ajax-search-species'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/pick-sightings/$',
        'zoo.trips.views.pick_sightings_for_place',
        name='place-pick_sightings_for_place'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/add-sightings/$',
        'zoo.trips.views.finish_add_sightings_to_place',
        name='place-add_sightings_to_place'),
    
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/support/$',
        'zoo.places.views.support',
        name='place-support'),    
    
    url(r'^(?P<country_code>\w{2})/$', 'zoo.places.views.country',
        name='country'),
    url(r'^countries/$', 'zoo.places.views.all_countries',
        name='countries'),
    
    url(r'^404/$', direct_to_template, {'template':'404.html'}),
    url(r'^500/$', direct_to_template, {'template':'500.html'}),
)

urlpatterns += patterns('zoo.changerequests.views',
    url(r'moderation/', 'moderation_queue',
        name='admin-moderation'),
)

# User patterns come last, because they are greedy
urlpatterns += patterns('',
    url(r'^(?P<username>\w+)/$', accounts.profile,
        name='accounts-profile'),
    url(r'^(?P<username>\w+)/edit/$', accounts.profile_edit,
        name='accounts-profile-edit'),
    url(r'^(?P<username>\w+)/photos/$', 'zoo.photos.views.user_photos',
        name='user-photos'),
    url(r'^(?P<username>\w+)/photos/by-trip/$', 
        'zoo.photos.views.user_photos_by_trip',
        name='user-photos-by-trip'),
    url(r'^(?P<username>\w+)/photos/unassigned/$',
        'zoo.photos.views.user_photos_unassigned',
        name='user-photos-unassigned'),
    url(r'^(?P<username>\w+)/photos/(?P<photo_id>\d+)/$',
        'zoo.photos.views.photo',
        name='photo'),
    url(r'^(?P<username>\w+)/photos/(?P<photo_id>\d+)/edit/$',
        'zoo.photos.views.edit_photo',
        name='photo-edit'),
    url(r'^(?P<username>\w+)/photos/(?P<photo_id>\d+)/delete/$',
        'zoo.photos.views.delete_photo',
        name='photo-delete'),
    url(r'^(?P<username>\w+)/photos/(?P<photo_id>\d+)/set-species/$',
        'zoo.photos.views.set_species',
        name='photo-set-species'),
    
    url(r'^(?P<username>\w+)/tripbook/$', 'zoo.trips.views.tripbook',
        name='tripbook'),
    url(r'^(?P<username>\w+)/trip/(?P<trip_id>\d+)/$', 
        'zoo.trips.views.trip_view',
        name='trip-view'),
    url(r'^(?P<username>\w+)/trip/(?P<trip_id>\d+)/edit/$',
        'zoo.trips.views.edit_trip', name='edit-trip'),
    url(r'^(?P<username>\w+)/trip/(?P<trip_id>\d+)/add-sightings/$',
        'zoo.trips.add_trip.add_sightings_to_trip', name='add-sightings-to-trip'),
    url(r'^(?P<username>\w+)/trip/(?P<trip_id>\d+)/upload/$',
        photos.upload_trip, name='upload-photos-trip'),
    url(r'^(?P<username>\w+)/trip/(?P<trip_id>\d+)/delete/$', 
        'zoo.trips.views.trip_delete',
        name='trip-delete'),
)

urlpatterns += patterns('django.contrib.flatpages.views',
    url(r'^(?P<url>.*)$', 'flatpage', name='flatpage'),
)
