from django.contrib import admin
from zoo.places.models import Country, Place, Enclosure

class PlaceAdmin(admin.ModelAdmin):
    exclude = ['created_at', 'last_modified_at']

admin.site.register(Country)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Enclosure)
