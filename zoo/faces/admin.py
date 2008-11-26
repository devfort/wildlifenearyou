from django.contrib import admin

from zoo.faces.models import FaceArea, FacePart, FaceAreaCategory, \
    SpecialPermission

class FacePartAdmin(admin.ModelAdmin):
    list_display = ('image', 'description', 'area', 'preview')

    def preview(self, obj):
        return u'<img src="%s" width="150">' % obj.image.url
    preview.allow_tags = True

admin.site.register(FaceArea, list_display = ['name', 'category', 'order'])
admin.site.register(FaceAreaCategory)
admin.site.register(SpecialPermission)
admin.site.register(FacePart, FacePartAdmin)
