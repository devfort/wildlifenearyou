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
    created_by = models.ForeignKey(User, related_name='photos')
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
    is_visible = models.BooleanField(default=False)
    moderated_by = models.ForeignKey(
        User, related_name='photos_moderated', null=True, blank=True,
    )
    moderated_at = models.DateTimeField(null=True, blank=True)

    # WARNING: Denormalisation ahoy! We have a bit of a tough one here:
    # photos are encouraged to have 0 or more sightings, and a sighting
    # relates a photo to both a place, a trip AND a species.
    #
    # BUT... many of these relationships are optional - a sighting doesn't
    # have to be associated with a trip (though it does have to be with a 
    # species). Even worse, a photo might be taken that associates with just
    # a trip or just a place (e.g. "Me next to the Zoo entrance").
    #
    # So it's unavoidable that there will be multiple paths to a photo from a
    # place and a trip. We're just going to have to suck it up.
    #
    # One thing we will NOT do is allow photos to be directly related to
    # species. If you want to upload a photo of a Zebra, it has to go against
    # a sighting... which means it has to be associated with a place as well.
    # This   discourage people from uploading random stock photos (a bit)

    # Photos can optionally relate to a trip and/or a place
    trip = models.ForeignKey(Trip, null=True, blank=True,
        related_name='photos'
    )
    place = models.ForeignKey(Place, null=True, blank=True,
        related_name='photos', help_text="""
        Normally a photo would be associated with a place THROUGH a sighting
        - but if you take a picture of yourself next to the cotswald wildlife
        center sign that's a PLACE thing, not a SIGHTING thing.
        """
    )

    # Photos can belong to 0+ sightings
    sightings = models.ManyToManyField(
        'trips.Sighting', null=True, blank=True, related_name='photos'
    )

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

    def thumb_75_pull_left(self):
        return mark_safe(
            '<a href="%s" title="%s"><img class="pull-left" src="%s" alt="%s" width="75" height="75"></a>' % (
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
