from django.db import models
from django.contrib.auth.models import User
from zoo.animals.models import Species
from zoo.places.models import Place
from zoo.trips.models import Trip
from zoo.utils import attrproperty

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
    
    # Photos can optionally relate to a trip and/or a place
    trip = models.ForeignKey(Trip, null = True, blank = True, 
        related_name = 'photos'
    )
    place = models.ForeignKey(Place, null = True, blank = True, 
        related_name = 'photos'
    )
    
    # There may be several species in a single photo
    contained_species = models.ManyToManyField(Species, blank=True)
    
    def __unicode__(self):
        return self.title or unicode(self.photo)
    
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
