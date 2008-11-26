from django.contrib import admin

from zoo.changerequests.models import ChangeRequestGroup, ChangeRequest, \
    ChangeAttributeRequest, DeleteObjectRequest

class ChangeRequestAdmin(admin.ModelAdmin): pass
class ChangeRequestGroupAdmin(admin.ModelAdmin): pass
class ChangeAttributeRequestAdmin(admin.ModelAdmin): pass
class DeleteObjectRequestAdmin(admin.ModelAdmin): pass

admin.site.register(ChangeRequest, ChangeRequestAdmin)
admin.site.register(ChangeRequestGroup, ChangeRequestGroupAdmin)
admin.site.register(ChangeAttributeRequest, ChangeAttributeRequestAdmin)
admin.site.register(DeleteObjectRequest, DeleteObjectRequestAdmin)
