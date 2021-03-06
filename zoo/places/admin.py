from django.contrib import admin
from zoo.places.models import Country, Place, PlaceCategory, \
    Webcam, PlaceNews, PlaceOpening, Facility, PlaceFacility, Extra, \
    PlaceDirection, TransportTypes, Currency, PlacePrice
from zoo.common.models import exclude as excludees

class PlacePriceInline(admin.TabularInline):
    model = PlacePrice
    exclude = excludees
    
class PlaceDirectionInline(admin.TabularInline):
    model = PlaceDirection
    exclude = excludees

excludees_place = excludees
excludees_place.append('opening_times')

admin.site.register(PlaceCategory, 
    list_display = ('name', 'plural', 'slug', 'order'),
    list_editable = ('plural', 'slug', 'order'),
)
admin.site.register(Webcam, exclude = excludees)
admin.site.register(Facility, exclude = excludees)
admin.site.register(PlaceFacility, exclude = excludees)
admin.site.register(PlaceNews, exclude = excludees)
admin.site.register(Extra, exclude = excludees)
admin.site.register(PlacePrice, exclude = excludees)
admin.site.register(Place,
    exclude = excludees_place,
    list_filter = ('featured', 'is_unlisted', 'country'),
    list_display = (
        'known_as', 'legal_name', 'town', 'country', 'latitude', 'longitude',
        'is_unlisted'
    ),
    raw_id_fields = ('chosen_photo',),
    search_fields = (
        'known_as', 'legal_name', 'town', 'address_line_1', 'address_line_2'
    ),
    inlines = [PlacePriceInline,PlaceDirectionInline],
    prepopulated_fields = {'slug': ('known_as',)},
)
admin.site.register(PlaceOpening)