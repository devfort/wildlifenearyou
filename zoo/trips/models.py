from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User

import datetime
from django.utils import dateformat

from zoo.utils import attrproperty
from zoo.common.models import AuditedModel
from zoo.animals.models import Species
from zoo.places.models import Place

class Trip(AuditedModel):
    start = models.DateField(null=True, blank=True)
    start_accuracy = models.CharField(max_length = 5,
        choices = (
            ('day', 'to the day'),
            ('month', 'to the month'),
            ('year', 'to the year'),
        )
    )
    end = models.DateField(null=True, blank=True, help_text = """
        Not currently used
    """.strip())
    name = models.CharField(null=True, blank=True, max_length=100,
        help_text="A title for this trip. At least one of name or date must be provided."
    )
    description = models.TextField(blank=True)
    rating = models.CharField(max_length=1, blank=True, choices=[ (i,i) for i in range(1,6) ])
    species = models.ManyToManyField(Species, through='Sighting')
    place = models.ForeignKey(Place)
    
    class Meta:
        ordering = ['-start']
    
    def save(self, *args, **kwargs):
        if self.name == '' and self.start is None and self.end is None:
            self.name = 'Unnamed trip'
        elif self.end is None and self.start:
            self.end = self.start
        return super(Trip,self).save(args, kwargs)
    
    def get_absolute_url(self):
        return self.urls.absolute

    @attrproperty
    @models.permalink
    def urls(self, name):
        if name == 'absolute':
            return ('trip-view', (), {
                'username': self.created_by.username,
                'trip_id': self.id,
            })
        elif name == 'edit':
            return ('edit-trip', (), {
                'username': self.created_by.username,
                'trip_id': self.id,
            })
        elif name == 'add_sightings':
            return ('add-sightings-to-trip', (), {
                'username': self.created_by.username,
                'trip_id': self.id,
            })
        else:
            raise AttributeError, name
    
    # THIS MUST BE static. It does not act on an instance and is called from
    # the profile model
    @staticmethod
    def get_passport(user):
        class Passport:
            def __init__(self, seen, favourites):
                self.seen_species = seen
                self.favourite_species = favourites

        if not user.is_authenticated():
            return Passport([])

        by_count = {}
        for species in Species.objects.filter(trip__created_by=user):
            by_count[species] = by_count.get(species, 0) + 1

        species_list = by_count.keys()

        for species in species_list:
            species.count = by_count[species]

        species_list.sort(key=lambda s: s.count, reverse=True)
        favourites = Species.objects.filter(favourited__user=user).order_by('?')

        return Passport(species_list, favourites)

    def formatted_start_date(self):
        date = self.start
        if date is not None:
            if self.start_accuracy == 'year':
                date = u'%s' % self.start.year
            elif self.start_accuracy == 'month':
                date = u'%s' % dateformat.format(self.start, 'F Y')
            else:
                date = u'%s' % dateformat.format(self.start, 'jS F Y')
        else:
            date = ''
        return date

    def formatted_date(self):
        date = self.start
        if date is not None:
            if self.start_accuracy == 'year':
                date = u' in %s' % self.start.year
            elif self.start_accuracy == 'month':
                date = u' in %s' % dateformat.format(self.start, 'F Y')
            else:
                date = u'%s' % dateformat.format(self.start, 'jS F Y')
            
                # now see if we need to add the end date
                if self.end > self.start:
                    # now check if month and year are the same
                    if dateformat.format(self.start, 'mY') == dateformat.format(self.end, 'mY'):
                        date = u' from %s to %s' % (dateformat.format(self.start, 'jS'), dateformat.format(self.end, 'jS F Y'))
                    elif self.start.year == self.end.year:
                        date = u' from %s to %s' % (dateformat.format(self.start, 'jS F'), dateformat.format(self.end, 'jS F Y'))
                    else:
                        date = u' from %s to %s' % (date, dateformat.format(self.end, 'jS F Y'))
                else:
                    date = u' on %s' % date
        else:
            date = ''
            
        return date
        
    def title(self, include_date=True):
        name = self.name or u'A trip '
        place = u' to %s' % self.place.known_as
        
        if include_date:
            date = self.formatted_date()
        else:
            date = u''
        
        # Multiple conditions allowed here
        return u'%s%s%s' % (name, place, date)
    
    def title_no_date(self):
        return self.title(include_date=False)
    
    def compact_title(self):
        name = self.name or 'A trip'
        date = self.formatted_date()
        return u'%s%s' % (name, date)

    @staticmethod
    def get_average_rating(place):
        trips = Trip.objects.filter(place = place, rating__gt = 0)
        return Trip.calculate_rating_object(trips)

    @staticmethod
    def get_my_average_rating_for_place(user, place):
        trips = Trip.objects.filter(
            place = place, created_by = user, rating__gt = 0
        )
        return Trip.calculate_rating_object(trips)

    @staticmethod
    def calculate_rating_object(trips):
        total_rating = sum([ int(trip.rating) for trip in trips if trip.rating ])
        rating = 0
        if len(trips):
            rating = int( (total_rating + 0.0) / len(trips) + 0.5 )
        # List uniquification from <http://www.peterbe.com/plog/uniqifiers-benchmark/uniqifiers_benchmark.py>
        # (I just chose the faster one, f9.)
        spotters = {}.fromkeys(map(lambda x: x.created_by, trips)).keys()
        rating = {
            'on': [ 1 for x in range(rating) ],
            'off': [ 1 for x in range(5-rating) ],
            'trips': len(trips),
            'spotters': len(spotters),
        }
        return rating  
    
    def visible_photos(self):
        return self.photos.filter(is_visible = True)
    
    @property
    def photo(self):
        try:
            return self.visible_photos.annotate(
                num_faves = Count('favourited')
            ).order_by('-num_faves')[0]
        except IndexError:
            return None
    
    def random_photo(self):
        vp = self.visible_photos()
        if vp.count():
            return vp.order_by('?')[0]
        return None
        
    def __unicode__(self):
        #return u"%s, %s" % (self.created_by.username, self.name)
        return self.title()
    
    def more_than_three_species(self):
        return self.species.all().distinct().count() > 3

class Sighting(AuditedModel):
    trip = models.ForeignKey(Trip, null=True, blank=True,
        help_text="""
            If this sighting was part of a trip, give it here. Leave blank for 
            a non-trip sighting, e.g. just <em>knowledge</em> about the
            species at this place
        """, related_name = 'sightings'
    )
    place = models.ForeignKey('places.Place',
        help_text="The place at which this sighting occurred",
    )
    # If what they saw doesn't exist in our species table, they can save a 
    # textual description instead. We'll provide tools to help people go 
    # back over their inexact matches and look them up properly at some point
    species = models.ForeignKey(Species,
        help_text="What was sighted", related_name='sightings',
        null=True, blank=True
    )
    species_inexact = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        super(Sighting, self).save(*args, **kwargs)
        # re-index the place in Xapian
        self.place.save()

    def visible_photos(self):
        return self.photos.filter(is_visible = True)
    
    def species_name(self):
        if self.species:
            return self.species.common_name
        else:
            return self.species_inexact
    
    def __unicode__(self):
        ret = u'Sighting of %s at %s' % (self.species_name(), self.place)
        if self.trip:
            ret += u' during trip %s' % self.trip
        return ret
