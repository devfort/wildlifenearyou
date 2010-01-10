from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.html import escape

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
        blank=True, # This will be blank for flickr photos
        upload_to='photos',
        thumbnail={'size': (75, 75), 'options': ('crop', 'upscale')},
        extra_thumbnails={
            'admin': {'size': (70, 50), 'options': ('sharpen',)},
            't': {'size': (100, 100), 'options': ('sharpen',)},
        }
    )
    # If the photo lives on Flickr, we store those details instead
    flickr_id = models.CharField(max_length=32, blank=True)
    flickr_secret = models.CharField(max_length=32, blank=True)
    flickr_server = models.CharField(max_length=16, blank=True)
    
    # Moderation flags
    is_visible = models.BooleanField(default=True)
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
    
    def thumb_75_img(self, extra_class=''):
        title = escape(self.detailed_title())
        if extra_class:
            extra_class = 'class="%s" ' % extra_class
        return mark_safe(
            '<img src="%s" alt="%s" %swidth="75" height="75">' % (
                self.thumb_75_url(),
                title,
                extra_class,
            )
        )
    
    def thumb_75(self, extra_class=''):
        title = escape(self.detailed_title())
        return mark_safe(
            '<a href="%s" title="%s">%s</a>' % (
                self.get_absolute_url(),
                title,
                self.thumb_75_img(),
            )
        )

    def thumb_75(self, extra_class=''):
        title = escape(self.detailed_title())
        return mark_safe(
            '<a href="%s" title="%s"%s>%s</a>' % (
                self.get_absolute_url(),
                title,
                extra_class and ' class="%s"' % extra_class or '',
                self.thumb_75_img(),
            )
        )

    def thumb_75_pull_left(self):
        return self.thumb_75(extra_class = 'pull-left')
    
    def thumb_100_url(self):
        if self.flickr_id:
            return 'http://static.flickr.com/%(flickr_server)s/%(flickr_id)s_%(flickr_secret)s_t.jpg' % self.__dict__
        else:
            return self.photo.extra_thumbnails['t'].absolute_url
    
    def thumb_75_url(self):
        if self.flickr_id:
            return 'http://static.flickr.com/%(flickr_server)s/%(flickr_id)s_%(flickr_secret)s_s.jpg' % self.__dict__
        else:
            return self.photo.thumbnail.absolute_url
    
    def original_url(self):
        if self.photo:
            return self.photo.url
        else:
            return 'http://www.flickr.com/photo.gne?id=%s' % self.flickr_id
    
    def detailed_title(self):
        species = list(
            Species.objects.filter(sightings__photos = self).distinct()
        )
        title = ''
        if self.title and not self.title.lower().endswith('.jpg'):
            title = '"%s"' % self.title
            if species:
                title += ': '
        if species:
            title += ', '.join([s.common_name for s in species])
        if title:
            title += (', by %s' % self.created_by)
        else:
            title = ('Photo by %s' % self.created_by)
        return title
    
    objects = models.Manager()
    visible = VisiblePhotoManager()

    def is_favourited_by(self, user):
        if not user.is_authenticated():
            return False
        return user.favourite_photos.filter(photo = self).count() > 0

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
