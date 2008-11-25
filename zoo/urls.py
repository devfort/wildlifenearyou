from django.conf.urls.defaults import *
from django.conf import settings
from django import http

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

from accounts import views as accounts
from faces import views as faces
from photos import views as photos

urlpatterns = patterns('',
    # Example:
    # (r'^zoo/', include('zoo.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': os.path.join(settings.OUR_ROOT, 'static')
    }),

    # Landing Page
    url(r'^$', 'zoo.homepage.views.landing',
        name='landing-page'),

    # User accounts stuff
    url(r'^login/$', 'django.contrib.auth.views.login', {
        'template_name': 'accounts/login.html'
    }, name='accounts-login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {
        'next_page': '/login/'
    }, name='accounts-logout'),
    url(r'^register/$', accounts.register,
        name='accounts-register'),
    url(r'^welcome/$', accounts.welcome,
        name='accounts-welcome'),

    url(r'^profile/$', accounts.profile_default,
        name='accounts-default'),
    url(r'^profile/(?P<username>\w+)/$', accounts.profile,
        name='accounts-profile'),
    url(r'^profile/(?P<username>\w+)/edit/$', accounts.profile_edit,
        name='accounts-profile-edit'),
    url(r'^profile/(?P<username>\w+)/photos/(?P<photo_id>\d+)/$',
        'zoo.photos.views.photo',
        name='photo'),

    url(r'^logbook/$', 'zoo.trips.views.logbook_default',
        name='logbook-default'),
    url(r'^profile/(?P<username>\w+)/logbook/$', 'zoo.trips.views.logbook',
        name='logbook'),
    url(r'^profile/(?P<username>\w+)/logbook/edit/$', 'zoo.trips.views.logbook_edit',
        name='logbook-edit'),
        
        

    url(r'^profiles/$', accounts.all_profiles,
        name='accounts-all-profiles'),

    (r'^faces/profile-images.xml$', faces.profile_images_xml),

    (r'^photos/upload/$', photos.upload),
    (r'^photos/$', photos.all),

    (r'^set-location/$', 'zoo.geonames.views.set_location'),
    (r'^geonames/autocomplete/$', 'zoo.geonames.views.autocomplete'),

    (r'^comments/', include('django.contrib.comments.urls')),

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

    url(r'^latin/$', 'zoo.animals.views.all_species_latin',
        name='all-species-latin'),
    url(r'^latin/(?P<latin_name>[^/]+)/$', 'zoo.animals.views.species_latin',),

    url(r'^(?P<country_code>\w{2})/(?P<slug>.*?)/upload/$',
        'zoo.photos.views.upload_place',
        name='place-upload'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>.*?)/$', 'zoo.places.views.place',
        name='place'),
    url(r'^places/$', 'zoo.places.views.all_places',
        name='places'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+?)/species$', 'zoo.places.views.place_species',
        name='place-species'),

    url(r'^(?P<country_code>\w{2})/$', 'zoo.places.views.country',
        name='country'),
    url(r'^countries/$', 'zoo.places.views.all_countries',
        name='countries'),
)
