from django.contrib import admin
from zoo.places.models import Country, Place, Enclosure, EnclosureSpecies, \
    Webcam, PlaceNews, PlaceOpening
from zoo.models import exclude as excludees

class EnclosureSpeciesInline(admin.TabularInline):
    model = EnclosureSpecies
    exclude = excludees

class EnclosureAdmin(admin.ModelAdmin):
    list_display = ('name', 'place')
    exclude = excludees
    inlines = [
        EnclosureSpeciesInline,
    ]

class PlaceInline(admin.TabularInline):
    model = Enclosure
    exclude = excludees

excludees_place = excludees
excludees_place.append('opening_times')

admin.site.register(Webcam, exclude = excludees)
admin.site.register(PlaceNews, exclude = excludees)
admin.site.register(Place,
    exclude = excludees_place,
    list_filter = ['country'],
    list_display = ('known_as', 'legal_name', 'town', 'country'),
    search_fields = ['known_as', 'legal_name', 'town', 'address_line_1', 'address_line_2'],
    inlines = [PlaceInline],
    prepopulated_fields = {'slug': ('known_as',)},
)
admin.site.register(Enclosure, EnclosureAdmin)
admin.site.register(PlaceOpening)
