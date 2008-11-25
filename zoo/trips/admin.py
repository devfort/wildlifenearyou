from django.contrib import admin
from zoo.trips.models import Trip, Sighting

#class TripSightingInline(admin.TabularInline):
#    model = TripSighting


admin.site.register(Trip,
#                   inlines = [TripSightingInline],
                    )
admin.site.register(Sighting)
