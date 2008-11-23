from django.conf.urls.defaults import *
from django.conf import settings
from django import http

import os

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^zoo/', include('zoo.foo.urls')),
    
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': os.path.join(settings.OUR_ROOT, 'static')
    }),
    
    # Dodo
    (r'^animals/dodo/$', 
        lambda r: http.HttpResponseGone('410 Gone')
    ),
    (r'^latin/raphus-cucullatus/$', 
        lambda r: http.HttpResponseRedirect('/animals/dodo/')
    ),
    
    # Django built-in admin
    (r'^admin/(.*)', admin.site.root),
)
