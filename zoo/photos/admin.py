from django.contrib import admin
from zoo.photos.models import Photo

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'preview', 'created_by', 'created_at')
    list_filter = ('created_at',)

    def preview(self, obj):
        return obj.photo.thumbnail_tag
    preview.allow_tags = True

admin.site.register(Photo, PhotoAdmin)
