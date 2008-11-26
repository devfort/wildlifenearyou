from django.contrib import admin
from zoo.accounts.models import Profile, Badge, ProfileBadge
from zoo.models import exclude as excludees

class ProfileBadgeInline(admin.TabularInline):
    model = ProfileBadge
    exclude = excludees

admin.site.register(Badge, exclude = excludees)
admin.site.register(Profile,
    exclude = excludees,
    inlines = [ProfileBadgeInline],
#    list_filter = ['country'],
#    list_display = ('known_as', 'legal_name', 'town', 'country'),
#    search_fields = ['known_as', 'legal_name', 'town', 'address_line_1', 'address_line_2'],
#    inlines = [PlaceInline, PlacePriceInline,],
#    prepopulated_fields = {'slug': ('known_as',)},
)
