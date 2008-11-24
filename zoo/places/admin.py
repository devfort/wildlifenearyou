from django.contrib import admin
from zoo.places.models import Country, Place, Enclosure, EnclosureSpecies, \
    Webcam, PlaceNews

excludees = ['created_at', 'created_by', 'modified_at', 'modified_by']

class EnclosureSpeciesInline(admin.TabularInline):
    model = EnclosureSpecies
    exclude = excludees

class EnclosureAdmin(admin.ModelAdmin):
    list_display = ('name', 'place')
    inlines = [
        EnclosureSpeciesInline,
    ]

    def changelist_view(self, request):
        #import pdb; pdb.set_trace()
        return super(EnclosureAdmin, self).changelist_view(request)

class PlaceInline(admin.TabularInline):
    model = Enclosure
    exclude = excludees

admin.site.register(Webcam)
admin.site.register(PlaceNews, exclude = excludees)
admin.site.register(Place,
    exclude = excludees,
    list_filter = ['country'],
    list_display = ('known_as', 'legal_name', 'town', 'country'),
    search_fields = ['known_as', 'legal_name', 'town', 'address_line_1', 'address_line_2'],
    inlines = [PlaceInline],
    prepopulated_fields = {'slug': ('known_as',)},
)
admin.site.register(Enclosure, EnclosureAdmin)
