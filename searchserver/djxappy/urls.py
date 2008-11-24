from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^djxappy/', include('djxappy.apps.foo.urls.foo')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
    (r'^search/', "search.search"),
    (r'^newdb/', "search.newdb"),
    (r'^deldb/', "search.deldb"),
    (r'^add/', "search.add"),
)
