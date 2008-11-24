from django.contrib import admin
from zoo.places.models import Country, Place, Enclosure, EnclosureAnimal, \
    Webcam

class PlaceAdmin(admin.ModelAdmin):
    exclude = ['created_at', 'modified_at']
    list_filter = ['country', 'town']
    search_fields = ['known_as', 'legal_name']

class EnclosureAnimalInline(admin.TabularInline):
    model = EnclosureAnimal

class EnclosureAdmin(admin.ModelAdmin):
    inlines = [
        EnclosureAnimalInline,
    ]

admin.site.register(Country)
admin.site.register(Webcam)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Enclosure, EnclosureAdmin)
