from django.contrib import admin
from zoo.animals.models import Species, SpeciesGroup

admin.site.register(Species,
    list_display = ('common_name', 'species_group', 'latin_name', 'slug'),
    list_filter = ['species_group'],
    search_fields = ['common_name', 'latin_name'],
    prepopulated_fields = {'slug': ('common_name',)},
)
admin.site.register(SpeciesGroup)
