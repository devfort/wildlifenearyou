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
    
    (r'^static/(?P<path>.*)$(?i)', 'django.views.static.serve', {
        'document_root': os.path.join(settings.OUR_ROOT, 'static')
    }),
    
    # User accounts stuff
    url(r'^login/$(?i)', 'django.contrib.auth.views.login', {
        'template_name': 'accounts/login.html'
    }, name='accounts-login'),
    url(r'^register/$(?i)', accounts.register, 
        name='accounts-register'),
    url(r'^welcome/$(?i)', accounts.welcome, 
        name='accounts-welcome'),
    url(r'^profile/(\w+)/$(?i)', accounts.profile, 
        name='accounts-profile'),
    url(r'^profile/(\w+)/edit/$(?i)', accounts.profile_edit, 
        name='accounts-profile-edit'),
   
    # Dodo
    (r'^animal/dodo/$(?i)', 
        lambda r: http.HttpResponseGone('410 Gone')
    ),
    (r'^latin/raphus-cucullatus/$(?i)', 
        lambda r: http.HttpResponseRedirect('/animal/dodo/')
    ),
    
    # Django built-in admin
    (r'^admin/(.*)', admin.site.root),

    # Databrowse
    (r'^databrowse/(.*)', databrowse.site.root),


    url(r'^animal/(?P<slug>[^/]+)/$(?i)', 'zoo.animals.views.animal',
        name='animal'),

    url(r'^latin/(?P<latin_name>[^/]+)/$(?i)', 'zoo.animals.views.animal_latin',),

#    url(r'^(?P<country_code>.*)/(?P<slug>.*)/$', 'zoo.places.views.place',
#        name='place'),

)
