from django.contrib import admin
from zoo.trips.models import Trip, TripSighting

class TripSightingInline(admin.TabularInline):
    model = TripSighting


admin.site.register(Trip,
                    inlines = [TripSightingInline],
                    )
admin.site.register(TripSighting)
