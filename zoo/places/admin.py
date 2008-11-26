from django.contrib import admin
from zoo.places.models import Country, Place, \
    Webcam, PlaceNews, PlaceOpening, Facility, PlaceFacility, Extra, \
    PlaceDirection, Currency, PlacePrice
from zoo.models import exclude as excludees

class PlacePriceInline(admin.TabularInline):
    model = PlacePrice
    exclude = excludees

excludees_place = excludees
excludees_place.append('opening_times')

admin.site.register(Webcam, exclude = excludees)
admin.site.register(Facility, exclude = excludees)
admin.site.register(PlaceFacility, exclude = excludees)
admin.site.register(PlaceNews, exclude = excludees)
admin.site.register(PlaceDirection, exclude = excludees)
admin.site.register(Extra, exclude = excludees)
admin.site.register(PlacePrice, exclude = excludees)
admin.site.register(Place,
    exclude = excludees_place,
    list_filter = ['country'],
    list_display = ('known_as', 'legal_name', 'town', 'country'),
    search_fields = ['known_as', 'legal_name', 'town', 'address_line_1', 'address_line_2'],
    inlines = [PlacePriceInline,],
    prepopulated_fields = {'slug': ('known_as',)},
)
admin.site.register(PlaceOpening)
