from django.db import models
from django.template.defaultfilters import pluralize
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from zoo.utils import attrproperty
from zoo.models import AuditedModel
#from zoo.trips.models import Trip

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
        
class Place(AuditedModel):
    legal_name = models.CharField(max_length=500, null=False, blank=False)
    known_as = models.CharField(max_length=500, null=False, blank=False)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    slug = models.SlugField(max_length=255, null=False, blank=False,
        unique=True
    )
    country = models.ForeignKey(Country, null=False, blank=False)

    # XXX Would this now work?
    #animals = models.ManyToManyField(Species, through='Sighting')
    #trips = models.ManyToManyField('trips.Trip', through='Sighting')

    opening_times = models.TextField()
    facilities = models.ManyToManyField('Facility', through='PlaceFacility')

    address_line_1 = models.CharField(max_length=250, null=True, blank=True)
    address_line_2 = models.CharField(max_length=250,  null=True, blank=True)
    town = models.CharField(max_length=250, null=True, blank=True)
    state = models.CharField(max_length=250, null=True, blank=True)
    zip = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)

    def address(self):
        bits = []
        for attr in (
            'address_line_1', 'address_line_2', 'town', 'state', 'zip',
            'country'
            ):
            val = unicode(getattr(self, attr, None))
            if val:
                bits.append(val)
        return ', '.join(bits)

    # long and lot for mapping
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    
    @models.permalink
    def get_absolute_url(self):
        return ('place', (), {
            'country_code': self.country.country_code.lower(),
            'slug': self.slug,
        })

    @attrproperty
    def urls(self, name):
        if name == 'absolute':
            return self.get_absolute_url()
    
    def visible_photos(self):
        return self.photos.filter(is_visible = True)
    
    def __unicode__(self):
        return self.known_as

def create_place_callback(sender, instance, created, **kwargs):
    # Create default nameless enclosure when place is created.
    if created:
        Enclosure.objects.create(place=instance)
post_save.connect(create_place_callback, sender=Place)

class Facility(models.Model):
    icon = models.ImageField(upload_to='facility_icons')
    default_desc = models.CharField(max_length=200, blank=True, null=True)

    def __unicode__(self):
        return self.default_desc

class PlaceFacility(AuditedModel):
    place = models.ForeignKey(Place, related_name='place_facilities')
    facility = models.ForeignKey(Facility)
    specific_desc = models.CharField(max_length=200, blank=True, null=True)

    @property
    def desc(self):
        return self.specific_desc or self.facility.default_desc

    def __unicode__(self):
        return self.desc

class PlaceNews(AuditedModel):
    place = models.ForeignKey(Place, related_name='news')
    headline = models.CharField(max_length=300)
    url = models.URLField(verify_exists=False)
    story_date = models.DateField()

    class Meta:
        verbose_name_plural = 'place news'

    def __unicode__(self):
        return u'%s (%s on %s)' % (self.headline, self.place, self.story_date)

class PlaceDirection(AuditedModel):
    place = models.ForeignKey(Place, related_name='direction')
    mode = models.CharField(max_length=50, null=False, blank=False)
    route = models.TextField()
    
    def __unicode__(self):
        return u'by %s: %s' % (self.mode, self.route)
        
class Webcam(AuditedModel):
    place = models.ForeignKey(Place, related_name='webcams')
    name = models.CharField(max_length=300, null=True, blank=True)
    url = models.URLField()

    def __unicode__(self):
        return self.name

class Enclosure(AuditedModel):
    place = models.ForeignKey(Place, related_name='enclosures')
    species = models.ManyToManyField('animals.Species', through='EnclosureSpecies')
    name = models.CharField(max_length=300, null=True, blank=True)

    def __unicode__(self):
        if self.name is None:
            return u"Nameless enclosure"
        return self.name

class EnclosureSpecies(AuditedModel):
    enclosure = models.ForeignKey(Enclosure)
    species = models.ForeignKey('animals.Species')
    number_of_inhabitants = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        retstr = self.species.common_name
        if self.number_of_inhabitants!=None:
            retstr += ' (%i)' % self.number_of_inhabitants
        if self.enclosure.name:
            retstr += ', %s' % self.enclosure.name
        retstr += ', %s' % self.enclosure.place.known_as
        return retstr

class PlaceOpening(models.Model):
    start_date = models.DateField(null=True, blank=True,
        help_text="Range of dates for which these times apply - leave either or both blank for an open-ended range",
    )
    end_date = models.DateField(null=True, blank=True)
    days_of_week = models.CharField(max_length=100, blank=True,
        help_text="Comma separated string of days this entry applies to, with 0=Sun, 6=Sat - e.g. 0,1,2,5 for Sun-Tue and Fri",
    )
    times = models.CharField(max_length=100, blank=True,
        help_text="Free form text field of times, e.g. 9am-5pm or dawn-dusk. Leave blank for all day",
    )
    closed = models.BooleanField(
        help_text="Whether this entry denotes a period when the place is closed",
    )
    place = models.ForeignKey(Place, null=False)
    section = models.CharField(max_length=255, blank=True,
        help_text="Section of the place this entry applies to, e.g. petting zoo - leave blank for entire place",
    )

    def __unicode__(self):
        closed = self.closed and 'closed ' or 'open'
        start_date = self.start_date or '*'
        end_date = self.end_date or '*'
        section = self.section and ('%s, ' % self.section) or ''
        if self.days_of_week:
            days_of_week = self.days_of_week.split(',')
            days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
            days_of_week = '/'.join([days[int(d)] for d in days_of_week])
        else:
            days_of_week = 'all days'
        times = self.times or 'All day'
        return "%s%s, %s %s %s-%s %s" % (section, self.place, closed, days_of_week, start_date, end_date, times)
