from django.db import models
from django.contrib.auth.models import User
from sorl.thumbnail.fields import ImageWithThumbnailsField

class Photo(models.Model):
    created_by = models.ForeignKey(User, related_name = 'photos')
    created_at =  models.DateTimeField()
    title = models.CharField(max_length=255, blank=True)
    photo = ImageWithThumbnailsField(
        upload_to='photos',
        thumbnail={'size': (100, 100), 'options': ('crop', 'upscale')},
        extra_thumbnails={
            'admin': {'size': (70, 50), 'options': ('sharpen',)},
        }
    )
    
    def __unicode__(self):
        return self.title or unicode(self.photo)
