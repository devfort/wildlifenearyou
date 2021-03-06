from django.contrib import admin
from zoo.animals.models import Species, SpeciesGroup, SuperSpecies
from zoo.common.models import exclude as excludes

admin.site.register(Species,
    list_display = (
        'common_name', 'species_group', 'latin_name', 'slug', 'freebase_id'
    ),
    list_filter = ['species_group', 'featured'],
    search_fields = ['common_name', 'latin_name'],
    prepopulated_fields = {'slug': ('common_name',)},
    exclude = excludes,
)
admin.site.register(SpeciesGroup,
    exclude = excludes,
)
admin.site.register(SuperSpecies,
    exclude = excludes,
    prepopulated_fields = {'slug': ('common_name',)},
)
