from django.contrib import admin

from zoo.changerequests.models import ChangeRequestGroup, ChangeRequest, \
    ChangeAttributeRequest

class ChangeRequestAdmin(admin.ModelAdmin): pass
class ChangeRequestGroupAdmin(admin.ModelAdmin): pass
class ChangeAttributeRequestAdmin(admin.ModelAdmin): pass

admin.site.register(ChangeRequest, ChangeRequestAdmin)
admin.site.register(ChangeRequestGroup, ChangeRequestGroupAdmin)
admin.site.register(ChangeAttributeRequest, ChangeAttributeRequestAdmin)
