from django.db import models
from photos.models import Photo

class FlickrSet(models.Model):
    user = models.ForeignKey('auth.User', related_name = 'flickr_sets')
    flickr_id = models.CharField(max_length = 100)
    title = models.CharField(max_length = 255)
    description = models.TextField(blank = True)
    photos = models.ManyToManyField(Photo, blank = True, null = True)
    
    def __unicode__(self):
        return u'%s (Flickr set %s)' % (self.title, self.flickr_id)
