from django.conf.urls.defaults import *
from django.conf import settings
from django import http

import os

from django.contrib import admin
admin.autodiscover()

from django.contrib import databrowse
from django.contrib.auth.models import User
from django.db.models import get_models
for model in get_models():
    databrowse.site.register(model)

from accounts import views as accounts

urlpatterns = patterns('',
    # Example:
    # (r'^zoo/', include('zoo.foo.urls')),
    
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': os.path.join(settings.OUR_ROOT, 'static')
    }),
    
    # User accounts stuff
    url(r'^login/$', 'django.contrib.auth.views.login', {
        'template_name': 'accounts/login.html'
    }, name='accounts-login'),
    url(r'^register/$', accounts.register, 
        name='accounts-register'),
    url(r'^welcome/$', accounts.welcome, 
        name='accounts-welcome'),
    url(r'^profile/(\w+)/$', accounts.profile, 
        name='accounts-profile'),
    url(r'^profile/(\w+)/edit/$', accounts.profile_edit, 
        name='accounts-profile-edit'),
    
    # Dodo
    (r'^animal/dodo/$', 
        lambda r: http.HttpResponseGone('410 Gone')
    ),
    (r'^latin/raphus-cucullatus/$', 
        lambda r: http.HttpResponseRedirect('/animal/dodo/')
    ),
    
    # Django built-in admin
    (r'^admin/(.*)', admin.site.root),

    # Databrowse
    (r'^databrowse/(.*)', databrowse.site.root),


    url(r'^animal/$', 'zoo.animals.views.animals',
        name='animals'),
    url(r'^animal/all\.xml$', 'zoo.animals.views.animals_xml',
        name='animals-xml'),
    url(r'^animal/(?P<slug>[^/]+)/$', 'zoo.animals.views.animal',
        name='animal'),

    url(r'^latin/(?P<latin_name>[^/]+)/$', 'zoo.animals.views.animal_latin',),

    url(r'^(?P<country_code>\w{2})/(?P<slug>.*)/$', 'zoo.places.views.place',
        name='place'),
    url(r'^(?P<country_code>\w{2})/$', 'zoo.places.views.country',
        name='country'),
)
