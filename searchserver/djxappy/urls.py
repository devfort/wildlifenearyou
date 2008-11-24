from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^djxappy/', include('djxappy.apps.foo.urls.foo')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
    (r'^xapian/(?P<db_name>\w+)/search/', "search.search"),
    (r'^xapian/newdb/', "search.newdb"),
    (r'^xapian/(?P<db_name>\w+)/deldb/', "search.deldb"),
    (r'^xapian/(?P<db_name>\w+)/add/', "search.add"),
)
