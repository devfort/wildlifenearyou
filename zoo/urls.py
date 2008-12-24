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
for model in get_models():
    if table_present(model._meta.db_table):
        databrowse.site.register(model)

from django.template import add_to_builtins
add_to_builtins('zoo.common.templatetags.switch')

from accounts import views as accounts
from faces import views as faces
from photos import views as photos

from accounts.openid import RegistrationConsumer

urlpatterns = patterns('',
    # Example:
    # (r'^zoo/', include('zoo.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': os.path.join(settings.OUR_ROOT, 'static')
    }),
    
    (r'^account/(.*?)$', RegistrationConsumer()),
    
    # Landing Page
    url(r'^$', 'zoo.homepage.views.landing',
        name='landing-page'),

    # shortcuts
    url(r'^tripbook/$', 'zoo.trips.views.tripbook_default',
        name='tripbook-default'),
    url(r'^profile/$', accounts.profile_default,
        name='accounts-default'),

    url(r'^search/$', 'zoo.search.views.search',
        name='search'),

    # Ajax autocompleters
    url(r'^autocomplete/species/(\d+)/$', 
        'zoo.trips.views.autocomplete_species',
        name='autocomplete-species-place'),

    # User accounts stuff
    url(r'^login/$', 'accounts.views.login', {
        'template_name': 'accounts/login.html'
    }, name='accounts-login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {
        'next_page': '/login/'
    }, name='accounts-logout'),

    url(r'^forgotten_password/$', 'accounts.views.forgotten_password',
        name='forgotten-password'),
    url(r'^password_key_sent/$', 'accounts.views.password_key_sent',
        name='password-key-sent'),
    url(r'^recover_password/(\w+)/([a-f0-9]+)/([a-f0-9]{32})/$', 'accounts.views.recover_password',
        name='recover-password'),
    url(r'^change_password/$', 'django.contrib.auth.views.password_change', {
            'template_name': 'accounts/change_password.html'
        }, name='change-password'),
    url(r'^change_password_done/$', 'django.contrib.auth.views.password_change_done', {
            'template_name': 'accounts/change_password_done.html'
        }, name='change-password-done'),

    url(r'^register/$', accounts.register,
        name='accounts-register'),
    url(r'^register/complete/$', accounts.registration_complete,
        name='accounts-registration-complete'),
    url(r'^register/validate/(\w+)/([a-f0-9]+)/([a-f0-9]{32})/$', 'accounts.views.validate_email',
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
    (r'^faces/(\w+).png$', faces.profile_image),
    url(r'^faces/small/(\w+).png$', faces.profile_image_resized,
        name="profile-image-resized",
        kwargs={ 'width': 30,
                 'height': 30,
                 }),
    (r'^faces/users/(\w+).xml$', faces.profile_image_xml),
    (r'^faces/update/$', faces.update),

    url(r'^flickr-callback/$', 'zoo.flickr.views.flickr_callback', 
        name='flickr-callback'),
    
    url(r'^photos/upload/$', photos.upload, name="upload-photos"),
    (r'^photos/$', photos.all),

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

    url(r'^animal/$', 'zoo.animals.views.all_species',
        name='all-species'),
    url(r'^animal/all\.xml$', 'zoo.animals.views.species_xml',
        name='species-xml'),
    url(r'^animal/(?P<slug>[^/]+)/$', 'zoo.animals.views.species',
        name='species'),

    url(r'^favourite/(?P<action>add|remove)/$', 'zoo.favourites.views.handle_favourite',
        name='favourite-species'),

    url(r'^latin/$', 'zoo.animals.views.all_species_latin',
        name='all-species-latin'),
    url(r'^latin/(?P<latin_name>[^/]+)/$', 'zoo.animals.views.species_latin',),

    url(r'^hit_parade/$', 'zoo.favourites.views.hit_parade',
        name='hit-parade'),

    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/upload/$',
        'zoo.photos.views.upload_place',
        name='place-upload'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/$', 'zoo.places.views.place',
        name='place'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>.*?)/suggest-changes/$',
        'zoo.places.views.place_edit', name='place-edit'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>.*?)/changes-suggested/$',
        'zoo.places.views.place_edit_done', name='place-edit-done'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>.*?)/summary/$', 'zoo.places.views.place_summary',
        name='place-summary'),

    url(r'^places/$', 'zoo.places.views.all_places',
        name='places'),
    url(r'^places/autocomplete/$', 'zoo.search.views.place_complete',
        name='places-autocomplete'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/species/$', 'zoo.places.views.place_species',
        name='place-species'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/species/(?P<species_slug>[^/]+)/$', 'zoo.places.views.place_species_view',
        name='place-species-view'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/add-trip/$',
        'zoo.trips.views.add_trip',
        name='place-add-trip'),
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
    url(r'^(?P<username>\w+)/photos/$', 'zoo.accounts.views.photos', name='accounts-profile-photos'),
    url(r'^(?P<username>\w+)/photos/(?P<photo_id>\d+)/$',
        'zoo.photos.views.photo',
        name='photo'),
    url(r'^(?P<username>\w+)/photos/(?P<photo_id>\d+)/edit/$',
        'zoo.photos.views.edit_photo',
        name='photo-edit'),
    url(r'^(?P<username>\w+)/photos/(?P<photo_id>\d+)/set-species/$',
        'zoo.photos.views.set_species',
        name='photo-set-species'),
    
    url(r'^(?P<username>\w+)/tripbook/$', 'zoo.trips.views.tripbook',
        name='tripbook'),
    url(r'^(?P<username>\w+)/trip/(?P<trip_id>\d+)/$', 'zoo.trips.views.trip_view',
        name='trip-view'),
    url(r'^(?P<username>\w+)/trip/(?P<trip_id>\d+)/upload/$',
        photos.upload_trip, name='upload-photos-trip'),
    url(r'^(?P<username>\w+)/trip/(?P<trip_id>\d+)/import-flickr/$',
        'zoo.flickr.views.import_trip', name='import-flickr-photos-trip'),
    url(r'^(?P<username>\w+)/trip/(?P<trip_id>\d+)/delete/$', 
        'zoo.trips.views.trip_delete',
        name='trip-delete'),
)

urlpatterns += patterns('django.contrib.flatpages.views',
    url(r'^(?P<url>.*)$', 'flatpage', name='flatpage'),
)


