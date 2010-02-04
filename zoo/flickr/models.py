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

class FlickrTagsApplied(models.Model):
    photo = models.ForeignKey('photos.Photo', 
        related_name='flickr_tags_applied'
    )
    tags_added = models.TextField(blank = True)
    latitude_added = models.FloatField(blank=True, null=True)
    longitude_added = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)
    
    def __unicode__(self):
        if self.tags_added:
            return u'Added tags %s to photo %s' % (
                self.tags_added, self.photo.pk
            )
        else:
            return u'Set location (%s, %s) for photo %s' % (
                self.latitude_added, self.longitude_added, self.photo.pk
            )
