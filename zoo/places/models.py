from django.db import models
from django.template.defaultfilters import pluralize
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from zoo.animals.models import Species
from zoo.utils import attrproperty

class Country(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    country_code = models.CharField(max_length=2, null=False, blank=False, unique=True)

    class Meta:
        verbose_name_plural = 'countries'
        
    @models.permalink
    def get_absolute_url(self):
        return ('country', (), {
            'country_code': self.country_code.lower()
        })

    @attrproperty
    def urls(self, name):
        if name == 'absolute':
            return self.get_absolute_url()

    def __unicode__(self):
        return self.name

class Place(models.Model):
    legal_name = models.CharField(max_length=500, null=False, blank=False)
    known_as = models.CharField(max_length=500, null=False, blank=False)
    slug = models.SlugField(max_length=255, null=False, blank=False,
        unique=True
    )
    country = models.ForeignKey(Country, null=False, blank=False)

    created_at = models.DateTimeField(null=False, blank=False)
    created_by = models.ForeignKey(User, related_name='places_created')
    modified_at = models.DateTimeField(null=False, blank=False)
    modified_by = models.ForeignKey(User, related_name='places_modified')

    # Address
    address_line_1 = models.CharField(max_length=250, null=True, blank=True)
    address_line_2 = models.CharField(max_length=250,  null=True, blank=True)
    town = models.CharField(max_length=250, null=True, blank=True)
    state = models.CharField(max_length=250, null=True, blank=True)
    zip = models.CharField(max_length=50, null=True, blank=True)

    def address(self):
        bits = []
        for attr in (
            'address_line_1', 'address_line_2', 'town', 'state', 'zip',
            'country'
            ):
            val = unicode(getattr(self, attr, None))
            if val:
                bits.append(val)
        return '\n'.join(bits)

    # long and lot for mapping
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)

    @models.permalink
    def get_absolute_url(self):
        return ('place', (), {
            'country_code': self.country.country_code,
            'slug': self.slug,
        })

    @attrproperty
    def urls(self, name):
        if name == 'absolute':
            return self.get_absolute_url()

    def __unicode__(self):
        return self.known_as

def create_place_callback(sender, instance, created, **kwargs):
    # Create default nameless enclosure when place is created.
    if created:
        Enclosure.objects.create(place=instance)
post_save.connect(create_place_callback, sender=Place)

class PlaceNews(models.Model):
    place = models.ForeignKey(Place, related_name = 'news')
    headline = models.CharField(max_length=300)
    url = models.URLField(verify_exists=False)
    story_date = models.DateField()
    
    created_at = models.DateTimeField(null=False, blank=False)
    created_by = models.ForeignKey(User, related_name = 'placenews_created')
    modified_at = models.DateTimeField(null=False, blank=False)
    modified_by = models.ForeignKey(User, related_name = 'placenews_modified')
    
    class Meta:
        verbose_name_plural = 'place news'
    
    def __unicode__(self):
        return u'%s (%s on %s)' % (self.headline, self.place, self.story_date)

class Webcam(models.Model):
    place = models.ForeignKey(Place, related_name = 'webcams')
    name = models.CharField(max_length=300, null=True, blank=True)
    url = models.URLField()

    def __unicode__(self):
        return self.name

class Enclosure(models.Model):
    place = models.ForeignKey(Place, related_name = 'enclosures')
    species = models.ManyToManyField(Species, through='EnclosureSpecies')
    name = models.CharField(max_length=300, null=True, blank=True)

    def __unicode__(self):
        if self.name is None:
            return u"Nameless enclosure"
        return self.name

class EnclosureSpecies(models.Model):
    enclosure = models.ForeignKey(Enclosure)
    species = models.ForeignKey(Species)
    number_of_inhabitants = models.IntegerField(null=True, blank=True)
    modified_at = models.DateTimeField(null=False, blank=False)
    modified_by = models.ForeignKey(User)

    def __unicode__(self):
        retstr = self.species.common_name
        if self.number_of_inhabitants!=None:
            retstr += ' (%i)' % self.number_of_inhabitants
        if self.enclosure.name:
            retstr += ', %s' % self.enclosure.name
        retstr += ', %s' % self.enclosure.place.known_as
        return retstr
