from django.contrib import admin
from zoo.places.models import Country, Place, Enclosure, EnclosureAnimal, \
    Webcam

excludees = ['created_at', 'created_by', 'modified_at', 'modified_by']

class EnclosureAnimalInline(admin.TabularInline):
    model = EnclosureAnimal
    exclude = excludees

class EnclosureAdmin(admin.ModelAdmin):
    list_display = ('name', 'place')
    inlines = [
        EnclosureAnimalInline,
    ]
    
    def changelist_view(self, request):
        #import pdb; pdb.set_trace()
        return super(EnclosureAdmin, self).changelist_view(request)

class PlaceInline(admin.TabularInline):
    model = Enclosure
    exclude = excludees

admin.site.register(Country)
admin.site.register(Webcam)
admin.site.register(Place, 
    exclude = excludees,
    list_filter = ['country', 'town'],
    search_fields = ['known_as', 'legal_name'],
    inlines = [PlaceInline]
)
admin.site.register(Enclosure, EnclosureAdmin)
