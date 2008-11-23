from django.contrib import admin
from zoo.animals.models import Animal, AnimalClass

admin.site.register(Animal)
admin.site.register(AnimalClass)
