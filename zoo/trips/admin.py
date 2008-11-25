from django.contrib import admin
from zoo.trips.models import Trip, Sighting
from zoo.models import exclude

class SightingInline(admin.TabularInline):
    model = Sighting
    exclude = exclude

admin.site.register(Trip,
    inlines = [SightingInline],
    exclude = exclude,
)
admin.site.register(Sighting,
    exclude = exclude,
)
