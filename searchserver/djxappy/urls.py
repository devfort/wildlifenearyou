from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    # Example:
    # (r'^djxappy/', include('djxappy.apps.foo.urls.foo')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),

    # Searching
    ('^' + settings.BASEURL + r'search/(?P<db_name>\w+)', "search.search"),

    # Database admin stuff
    ('^' + settings.BASEURL + r'listdbs', "search.listdbs"),
    ('^' + settings.BASEURL + r'newdb', "search.newdb"),
    ('^' + settings.BASEURL + r'deldb/(?P<db_name>\w+)', "search.deldb"),

    # Adding documents
    ('^' + settings.BASEURL + r'add/(?P<db_name>\w+)', "search.add"),
)
