from django.contrib import admin

from zoo.common.models import exclude
from zoo.trips.models import Trip, Sighting

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
