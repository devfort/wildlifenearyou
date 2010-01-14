from django.contrib import admin

from zoo.photos.models import Photo

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'preview', 'created_by', 'created_at', 'is_visible')
    list_filter = ('created_at', 'is_visible')
    
    raw_id_fields = (
        'created_by', 'moderated_by', 'trip', 'place', 'sightings'
    )
    
    def preview(self, obj):
        return obj.thumb_75()
    preview.allow_tags = True

admin.site.register(Photo, PhotoAdmin)
