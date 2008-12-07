from django.contrib import admin
from zoo.accounts.models import Profile, Badge, ProfileBadge
from zoo.common.models import exclude as excludees

class ProfileBadgeInline(admin.TabularInline):
    model = ProfileBadge
    exclude = excludees

admin.site.register(Badge, exclude = excludees)
admin.site.register(Profile,
    exclude = excludees,
    inlines = [ProfileBadgeInline],
    list_filter = ['featured'],
)
