from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.html import escape

from sorl.thumbnail.fields import ImageWithThumbnailsField

from zoo.trips.models import Trip
from zoo.utils import attrproperty
from zoo.places.models import Place
from zoo.animals.models import Species

import datetime

class VisiblePhotoManager(models.Manager):
    def get_query_set(self):
        return self.filter(is_visible = True)

class Photo(models.Model):
    created_by = models.ForeignKey(User, related_name='photos')
    created_at =  models.DateTimeField()
    title = models.CharField(max_length=255, blank=True)
    taken_at = models.DateTimeField(blank = True, null = True)
    photo = ImageWithThumbnailsField(
        blank=True, # This will be blank for flickr photos
        upload_to='photos',
        thumbnail={'size': (75, 75), 'options': ('crop', 'upscale')},
        extra_thumbnails={
            'admin': {'size': (70, 50), 'options': ('sharpen',)},
            't': {'size': (100, 100), 'options': ('sharpen',)},
            'm': {'size': (240, 240), 'options': ('sharpen',)},
        }
    )
    # If the photo lives on Flickr, we store those details instead
    flickr_id = models.CharField(max_length=32, blank=True)
    flickr_secret = models.CharField(max_length=32, blank=True)
    flickr_server = models.CharField(max_length=16, blank=True)
    
    has_no_species = models.NullBooleanField(null = True, default = False)
    
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
    # This discourage people from uploading random stock photos (a bit)
    
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
    
    def thumb_75_img(self, extra_class='', include_title=False):
        if extra_class:
            extra_class = 'class="%s" ' % extra_class
        return mark_safe(
            '<img src="%s" alt="%s" width="75" height="75"%s>' % (
                self.thumb_75_url(),
                extra_class,
                include_title and (' title="%s"' % escape(self.title)) or ''
            )
        )
    
    def thumb_75(self, extra_class='', include_title=False):
        return mark_safe(
            '<a href="%s"%s%s>%s</a>' % (
                self.get_absolute_url(),
                extra_class and ' class="%s"' % extra_class or '',
                include_title and (' title="%s"' % escape(self.title)) or '',
                self.thumb_75_img(),
            )
        )

    def thumb_75_pull_left(self, include_title=False):
        return self.thumb_75(
            extra_class = 'pull-left', include_title=include_title
        )
    
    def thumb_75_with_title(self):
        return self.thumb_75(include_title = True)
    
    def thumb_240_url(self):
        if self.flickr_id:
            return 'http://static.flickr.com/%(flickr_server)s/%(flickr_id)s_%(flickr_secret)s_m.jpg' % self.__dict__
        else:
            return self.photo.extra_thumbnails['m'].absolute_url
    
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

class SuggestedSpecies(models.Model):
    photo = models.ForeignKey(Photo, related_name = 'suggestions')
    species = models.ForeignKey(Species,
        related_name = 'suggestions', null = True, blank = True
    )
    species_inexact = models.CharField(max_length = 100, blank = True)
    suggested_by = models.ForeignKey(User, related_name = 'suggestions')
    suggested_at = models.DateTimeField()
    denorm_suggestion_for = models.ForeignKey(User,
        related_name = 'suggestions_for'
    )
    note = models.TextField(blank = True)
    status = models.CharField(max_length = 20, choices = (
        ('new', 'New'),
        ('approved', 'approved'),
        ('rejected', 'rejected'),
    ), default = 'new', db_index = True)
    status_changed_at = models.DateTimeField(null = True, blank = True)
    
    def is_new(self):
        return self.status == 'new'
    
    def is_approved(self):
        return self.status == 'approved'
    
    def is_rejected(self):
        return self.status == 'rejected'
    
    def approve(self):
        sightings = self.photo.sightings.all()
        defaults = {'place': self.photo.trip.place, 'note': ''}
        if self.species:
            sighting, created = self.photo.trip.sightings.get_or_create(
                species = self.species, defaults = defaults
            )
        else:
            sighting, created = photo.trip.sightings.get_or_create(
                species_inexact = self.species_inexact, defaults = defaults
            )
        self.photo.sightings.add(sighting)
        self.status_changed_at = datetime.datetime.now()
        self.status = 'approved'
        self.save()
    
    def reject(self):
        self.status_changed_at = datetime.datetime.now()
        self.status = 'rejected'
        self.save()
    
    def __unicode__(self):
        return u'%s suggested photo %s by user %s contains a %s' % (
            self.suggested_by, self.photo, self.denorm_suggestion_for,
            (self.species_inexact or self.species)
        )
