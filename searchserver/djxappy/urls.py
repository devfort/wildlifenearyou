from django.conf.urls.defaults import *
from django.conf import settings
import os

import search

urlpatterns = patterns('',
    # Example:
    # (r'^djxappy/', include('djxappy.apps.foo.urls.foo')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),

    ('^' + settings.BASEURL + r'latestapi', "search.latestapi"),

    # Searching
    ('^' + settings.BASEURL + search.api_version + r'search/(?P<db_name>\w+)', "search.search"),
    ('^' + settings.BASEURL + search.api_version + r'get/(?P<db_name>\w+)', "search.get"),
    ('^' + settings.BASEURL + search.api_version + r'parse_latlong', "search.parse_latlong"),

    # Database admin stuff
    ('^' + settings.BASEURL + search.api_version + r'listdbs', "search.listdbs"),
    ('^' + settings.BASEURL + search.api_version + r'newdb', "search.newdb"),
    ('^' + settings.BASEURL + search.api_version + r'deldb', "search.deldb"),

    # Adding documents
    ('^' + settings.BASEURL + search.api_version + r'add/(?P<db_name>\w+)', "search.add"),
    ('^' + settings.BASEURL + search.api_version + r'bulkadd/(?P<db_name>\w+)', "search.bulkadd"),
    
    # API explorer
    ('^' + settings.BASEURL + search.api_version + r'api-explorer/(?P<path>.*)$', 
        'django.views.static.serve', {
            'document_root': os.path.join(
                os.path.dirname(__file__), 'api-explorer'
            )
        },
    ),
)
