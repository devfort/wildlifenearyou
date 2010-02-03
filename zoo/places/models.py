from django.db import models
from django.db.models import Count
from django.template.defaultfilters import pluralize
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
from django.core.cache import cache

from zoo.utils import attrproperty
from zoo.common.models import AuditedModel
from zoo.shorturl.utils import converter

import geopy.distance

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

class Currency(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    currency_code = models.CharField(max_length=3, null=False, blank=False, unique=True)

    class Meta:
        verbose_name_plural = 'currencies'

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.currency_code)

def _species_for_place(place):
    from zoo.animals.models import Species # Avoid circular import
    return Species.objects.filter(
        sightings__place = place
    ).values_list('common_name', flat=True)

class Place(AuditedModel):
    legal_name = models.CharField(max_length=500, null=False, blank=False)
    known_as = models.CharField(max_length=500, null=False, blank=False)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True, verify_exists=False)
    slug = models.SlugField(max_length=255, null=False, blank=False,
        unique=True
    )
    country = models.ForeignKey(Country, null=False, blank=False)

    opening_times = models.TextField()
    facilities = models.ManyToManyField('Facility', through='PlaceFacility')

    address_line_1 = models.CharField(max_length=250, null=True, blank=True)
    address_line_2 = models.CharField(max_length=250,  null=True, blank=True)
    town = models.CharField(max_length=250, null=True, blank=True)
    state = models.CharField(max_length=250, null=True, blank=True)
    zip = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)

    price_notes = models.TextField(null=True, blank=True)

    featured = models.BooleanField(null=False, blank=False, default=False)
    
    # If a random user adds a place, it doesn't get marked as confirmed 
    # until a moderator has checked it. This will probably be the principle 
    # way that new places are added to the database.
    is_confirmed = models.BooleanField(default=False)
    
    #mapping stuff - and Grid Ref for reserves
    gridref = models.CharField(max_length=8, null=True, blank=True)
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    
    # We can (optionally) editorially select a photo to feature for this place
    chosen_photo = models.ForeignKey(
        'photos.Photo', null=True, blank=True,
        related_name='place_we_feature_for'
    )
    
    # External identifiers are useful
    freebase_id = models.CharField(max_length=100, blank=True, db_index=True)
    wikipedia_url = models.CharField(max_length=255, blank=True)
    
    @property
    def photo(self):
        photo = cache.get('photo-of-place:%s' % self.pk)
        if photo is None:
            if self.chosen_photo:
                photo = self.chosen_photo
            else:
                try:
                    photo = self.visible_photos().annotate(
                        num_faves = Count('favourited')
                    ).order_by('-num_faves')[0]
                except IndexError:
                    photo = 'no-photo'
            cache.set('photo-of-place:%s' % self.pk, photo, 60 * 60 * 5)
        
        if photo == 'no-photo':
            return None
        
        return photo
    
    def photo_of(self, species):
        key = 'photo-of-place-species:%s:%s' % (self.pk, species.pk)
        photo = cache.get(key)
        if photo is None:
            try:
                photo = self.visible_photos().filter(
                    sightings__species = species
                ).annotate(
                    num_faves = Count('favourited')
                ).order_by('-num_faves')[0]
            except IndexError:
                photo = 'no-photo'
            cache.set(key, photo, 60 * 60 * 5 + 5)
        if photo == 'no-photo':
            return None
        
        return photo
    
    def species_info(self, species):
        "Returns photo, num spottings and most recent trip - or None"
        key = 'place-species-info:%s:%s' % (self.pk, species.pk)
        info = cache.get(key)
        if info is None:
            photo = self.photo_of(species)
            sightings = species.sightings.filter(
                place = self
            ).select_related('trip', 'created_by').order_by('-created_at')
            num_sightings = sightings.count()
            most_recent_sighting = sightings[0]
            info = {
                'photo': photo,
                'num_sightings': num_sightings,
                'most_recent_user': most_recent_sighting.created_by,
                'most_recent_added_at': most_recent_sighting.created_at,
                'most_recent_trip': most_recent_sighting.trip,
            }
            cache.set(key, info, 60 * 60 * 7)
        return info
    
    def popularity(self):
        """
        Currently just calculated using number of species seen at
        this place.
        """

        by_count = {}
        for sighting in self.sightings.all():
            species = sighting.species
            by_count[species] = by_count.get(species, 0) + 1

        species_list = by_count.keys()
        for species in species_list:
            species.count = by_count[species]

        num_of_species = float(len(species_list))

        return 1 - (1 / (num_of_species + 1))

    def address(self):
        bits = []
        for attr in (
            'address_line_1', 'address_line_2', 'town', 'state', 'zip'
            ):
            val = unicode(getattr(self, attr, '') or '')
            if val:
                bits.append(val)
        return ', '.join(bits)
    
    def rough_location(self):
        if self.town:
            return self.town
        elif self.state:
            return self.state
        else:
            return None
    
    def random_photo(self):
        vp = self.visible_photos()
        if vp.count():
            return vp.order_by('?')[0]
        return None
    
    def latlon(self):
        if self.longitude is None or self.latitude is None:
            return ''
        return "%f %f" % (self.latitude, self.longitude)

    def get_absolute_url(self):
        return self.urls.absolute
    
    def short_url(self):
        return 'http://wlny.eu/p%s' % converter.from_int(self.pk)
    
    @attrproperty
    @models.permalink
    def urls(self, name):
        if name == 'absolute':
            urlname = 'place'
        elif name == 'summary':
            urlname = 'place-summary'
        elif name == 'animal_checklist':
            urlname = 'place-animal-checklist'
        elif name == 'suggest_changes':
            urlname = 'place-edit'
        elif name == 'changes_suggested':
            urlname = 'place-edit-done'
        elif name == 'species':
            urlname = 'place-species'
        else:
            raise AttributeError, 'No such url "%s"' % name
        return (urlname, (), {
            'country_code': self.country.country_code.lower(),
            'slug': self.slug,
            })

    def visible_photos(self):
        from zoo.photos.models import Photo
        return Photo.objects.filter(
            trip__place = self,
            is_visible = True
        ).distinct()

    def random_photo(self):
        vp = self.visible_photos()
        if vp.count():
            return vp.order_by('?')[0]
        return None

    class Searchable:
        fields = [
            { # Searching for places by name.
                'field_name': 'place',
                'django_fields': ['legal_name', 'known_as'],
                'config': {'store': True, 'freetext': {'language': 'en'}},
            #}, { # Searching the description.
            #    'field_name': 'description',
            #    'django_fields': ['description'],
            #    'config': {'store': True, 'freetext': {'language': 'en'}},
            }, { # Searching for the place address.
                'field_name': 'address',
                'django_fields': [lambda inst: [inst.address()], 'country'],
                'config': {'store': True, 'freetext': {'language': 'en'}},
            }, { # Searching for the animals in a place.
                # This expression should return all the common names of the
                # species sighted in the place.  Repeated sightings of a
                # particular species will result in duplicated entries,
                # which will correspond to a higher weight.
                'field_name': 'species',
                'django_fields': [_species_for_place], # see above
                'config': {
                    'freetext': {'language': 'en'},
                    'store': True,
                } # enable stemming
            }, { # Location of the place.
                'field_name': 'latlon',
                'django_fields': [lambda inst: [inst.latlon()]],
                'config': {'type': 'geo', 'geo': {}, 'store': True}
            }, { # Facilities of the place.
                'field_name': 'facilities',
                'django_fields': [
                                    lambda inst: [f.specific_desc for f in inst.place_facilities.all()],
                                    lambda inst: [f.facility.default_desc for f in inst.place_facilities.all()],
                                  ],
                'config': {
                    'freetext': {'language': 'en'},
                    'store': True,
                } # enable stemming,
            },
        ]
        xapian_index = 'placeinfo'

    def most_recent_trips(self):
        from zoo.trips.models import Trip
        trips = Trip.objects.filter(
            place = self
        ).order_by('-created_at')
        return trips

    def most_common_animal(self):
        "The animal with the most sightings"
        from zoo.animals.models import Species
        species_ids = list(
            self.sightings.values_list('species', flat=True)
        )
        if not species_ids:
            return None
        counts = dict([
            (species_id, species_ids.count(species_id))
            for species_id in species_ids
        ])
        pairs = counts.items()
        pairs.sort(key = lambda p: p[1], reverse=True)
        return Species.objects.get(pk = pairs[0][0])

    def __unicode__(self):
        return self.known_as

    def get_slug_suggestions(self):
        yield self.known_as
        yield self.town
        yield self.state

    def get_species(self, user=None, limit=None):
        """
        If user argument is provided, seen=True flag will be added to all
        species which have been seen by that user.
        """
        from zoo.trips.models import Trip, Sighting
        if user and not user.is_anonymous():
            seen_species = Trip.get_passport(user).seen_species
        else:
            seen_species = []

        by_count = {}
        for sighting in Sighting.objects.filter(
                place=self, species__isnull=False
            ).select_related('species'):
            species = sighting.species
            by_count[species] = by_count.get(species, 0) + 1

        if by_count.values():
            max_species = max(by_count.values())

        species_list = by_count.keys()
        for species in species_list:
            species.count = by_count[species]
            species.quad = int(4 * (by_count[species] - 1.0) / max_species)
            if species in seen_species:
                species.seen = True

        species_list.sort(key=lambda s: s.common_name)

        if limit:
            species_list = species_list[:limit]

        return species_list
    
    def num_visitors(self):
        "Number of unique people who have reported sightings at this zoo"
        return User.objects.filter(
            created_sighting_set__place = self
        ).distinct().count()

class DistanceBetween(models.Model):
    origin = models.ForeignKey(Place, related_name = 'nearby')
    place = models.ForeignKey(Place, related_name = 'nearby_rev')
    distance_km = models.FloatField(db_index = True)
    
    def distance(self):
        return geopy.distance.Distance(kilometers = self.distance_km)
    
    class Meta:
        ordering = ('distance_km',)
    
    def __unicode__(self):
        return u'%s is %skm away from %s' % (
            self.place, self.distance_km, self.origin
        )

class Facility(models.Model):
    icon = models.ImageField(upload_to='facility_icons')
    default_desc = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'facilities'

    def __unicode__(self):
        return self.default_desc

class PlaceFacility(AuditedModel):
    place = models.ForeignKey(Place, related_name='place_facilities')
    facility = models.ForeignKey(Facility)
    specific_desc = models.CharField(max_length=200, blank=True, null=True)

    @property
    def desc(self):
        return self.specific_desc or self.facility.default_desc

    class Meta:
        verbose_name_plural = 'place facilities'

    class Searchable:
        cascades = ['place']

    def __unicode__(self):
        return self.desc

class Extra(AuditedModel):
    place = models.ForeignKey(Place, related_name='extras')
    text_desc = models.CharField(max_length=200, blank=True, null=True)
    file = models.FileField(upload_to='places_extras')

    @property
    def display_filename(self):
        return self.file.name.split('/')[-1]

    @property
    def desc(self):
        return self.text_desc or self.display_filename

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

class TransportTypes(models.Model):
    icon = models.ImageField(upload_to='transport_icons')
    default_desc = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Modes of Transport'

    def __unicode__(self):
        return self.default_desc

class PlaceDirection(AuditedModel):
    place = models.ForeignKey(Place, related_name='direction')
    mode = models.ForeignKey(TransportTypes)
    route = models.TextField()

    def __unicode__(self):
        return u'by %s: %s' % (self.mode, self.route)

class Webcam(AuditedModel):
    place = models.ForeignKey(Place, related_name='webcams')
    name = models.CharField(max_length=300, null=True, blank=True)
    url = models.URLField()

    def __unicode__(self):
        return self.name

class PlacePrice(AuditedModel):
    place = models.ForeignKey(Place, related_name='price')
    currency = models.ForeignKey(Currency)
    type = models.CharField(max_length=100, null=False, blank=False)
    value = models.DecimalField(decimal_places=2, max_digits=12, null=False, blank=False)

    def __unicode__(self):
        return u'%s: %s%s' %(self.type, self.currency.currency_code, self.value)

class PlaceOpening(models.Model):
    start_date = models.DateField(null=True, blank=True,
        help_text="Range of dates for which these times apply - leave either or both blank for an open-ended range. Enter dates as YYYY-MM-DD.",
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
        return u"%s%s, %s %s %s-%s %s" % (section, self.place, closed, days_of_week, start_date, end_date, times)

# Seriously. We named this so you'd think about it. If you do anything with this, you could cause the end of the universe.
class PlaceSpeciesSolelyForLinking(models.Model):
    """
    Do not use this except for linking other entities in to a particular
    species at a zoo. Before you DO use it, have a long hard think about
    whether the sightings table would be a better place to link to.

    This was created because Django's comment system has to have a concrete
    object to connect to. We hope to never use it for anything else.

    This is NOT how we know if a species exists at a zoo; that is entirely
    derived from sightings (trips.Sighting).
    """
    place = models.ForeignKey(Place)
    species = models.ForeignKey('animals.Species')

    def visible_photos(self):
        from zoo.photos.models import Photo
        return Photo.objects.filter(
            sightings__place = self.place, 
            sightings__species = self.species
        ).filter(
            is_visible = True
        ).distinct()

    class Meta:
        db_table = 'places_placespecies'

    def __unicode__(self):
        return unicode(self.species.common_name) + u' at ' + unicode(self.place)
    
    @models.permalink
    def get_absolute_url(self):
        return ('place-species-view', (), {
            'country_code': self.place.country.country_code.lower(),
            'slug': self.place.slug,
            'species_slug': self.species.slug,
        })

    @attrproperty
    def urls(self, name):
        if name == 'absolute':
            return self.get_absolute_url()
