from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from sorl.thumbnail.fields import ImageWithThumbnailsField

from zoo.trips.models import Trip
from zoo.utils import attrproperty
from zoo.places.models import Place
from zoo.animals.models import Species

class VisiblePhotoManager(models.Manager):
    def get_query_set(self):
        return self.filter(is_visible = True)

class Photo(models.Model):
    created_by = models.ForeignKey(User, related_name = 'photos')
    created_at =  models.DateTimeField()
    title = models.CharField(max_length=255, blank=True)
    photo = ImageWithThumbnailsField(
        upload_to='photos',
        thumbnail={'size': (75, 75), 'options': ('crop', 'upscale')},
        extra_thumbnails={
            'admin': {'size': (70, 50), 'options': ('sharpen',)},
        }
    )
    
    # Moderation flags
    is_visible = models.BooleanField(default = False)
    moderated_by = models.ForeignKey(
        User, related_name = 'photos_moderated', null=True, blank=True,
    )
    moderated_at = models.DateTimeField(null=True, blank=True)

    # Photos can optionally relate to a trip and/or a place
    trip = models.ForeignKey(Trip, null=True, blank=True,
        related_name='photos'
    )
    place = models.ForeignKey(Place, null = True, blank = True,
        related_name='photos'
    )

    # There may be several species in a single photo
    contained_species = models.ManyToManyField(Species, blank=True)

    def __unicode__(self):
        return self.title or unicode(self.photo)
    
    def thumb_75(self):
        return mark_safe(
            '<a href="%s" title="%s"><img src="%s" alt="%s" width="75" height="75"></a>' % (
                self.get_absolute_url(),
                self.title or ('Photo by %s' % self.created_by),
                self.photo.thumbnail,
                self.title or ('Photo by %s' % self.created_by),
            )
        )
    
    objects = models.Manager()
    visible = VisiblePhotoManager()
    
    @models.permalink
    def get_absolute_url(self):
        return ('photo', (), {
            'username': self.created_by.username,
            'photo_id': self.id,
        })

    @attrproperty
    def urls(self, name):
        if name == 'absolute':
            return self.get_absolute_url()
