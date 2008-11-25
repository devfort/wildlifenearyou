from django.contrib import admin
from zoo.faces.models import FaceArea, FacePart

class FacePartAdmin(admin.ModelAdmin):
    list_display = ('image', 'area', 'preview')

    def preview(self, obj):
        return u'<img src="%s" width="150">' % obj.image.url
    preview.allow_tags = True

admin.site.register(FaceArea)
admin.site.register(FacePart, FacePartAdmin)
