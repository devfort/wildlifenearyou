from django.contrib import admin
from zoo.animals.models import Animal, AnimalClass

class AnimalAdmin(admin.ModelAdmin):
    list_display = ('common_name', 'animal_class', 'latin_name', 'slug')
    list_filter = ['animal_class']
    search_fields = ['common_name', 'latin_name']

class AnimalClassAdmin(admin.ModelAdmin):
    pass

admin.site.register(Animal, AnimalAdmin)
admin.site.register(AnimalClass, AnimalClassAdmin)
