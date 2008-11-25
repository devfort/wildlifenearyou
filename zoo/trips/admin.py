from django.contrib import admin
from zoo.trips.models import Trip, Sighting

class SightingInline(admin.TabularInline):
    model = Sighting


admin.site.register(Trip,
                   inlines = [SightingInline],
                    )
admin.site.register(Sighting)
