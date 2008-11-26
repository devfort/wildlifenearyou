from django.db import models
from django.contrib.auth.models import User

import datetime
from django.utils import dateformat

from zoo.utils import attrproperty
from zoo.models import AuditedModel
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
    species = models.ManyToManyField(Species, through='Sighting')

    class Meta:
        ordering = ['-start']

    def save(self, *args, **kwargs):
        if self.name == '' and self.start is None and self.end is None:
            self.name = 'Unnamed trip'
        elif self.end is None and self.start:
            self.end = self.start
        return super(Trip,self).save(args, kwargs)

    # THIS MUST BE static. It does not act on an instance and is called from
    # the profile model
    @staticmethod
    def get_passport(user):
        class Passport:
            def __init__(self, seen):
                self.seen_species = seen

        if not user.is_authenticated():
            return Passport([])

        by_count = {}
        for species in Species.objects.filter(trip__created_by=user):
            by_count[species] = by_count.get(species, 0) + 1

        species_list = by_count.keys()

        for species in species_list:
            species.count = by_count[species]

        species_list.sort(key=lambda s: s.count, reverse=True)

        return Passport(species_list)

    def formatted_date(self):
        date = self.start
        if date is not None:
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
            date = '';
            
        return date
        
    def title(self):
        name = self.name or 'A trip'
            
        p = Place.objects.filter(sighting__trip=self).distinct()
        if p.count() > 1:
            place = ' to multiple places'
        elif p.count() == 1:
            place = u' to %s' % p[0].known_as
        else:
            # This will only happen against broken old databases
            place = u' to place unknown'    
        date = self.formatted_date()
        
        # Multiple conditions allowed here
        return u'%s%s%s' % (name, place, date)

    def __unicode__(self):
        #return u"%s, %s" % (self.created_by.username, self.name)
        return self.title()

class Sighting(AuditedModel):
    place = models.ForeignKey('places.Place',
        help_text="The place at which this sighting occurred",
    )
    species = models.ForeignKey(Species,
        help_text="What was sighted",
    )
    trip = models.ForeignKey(Trip, null=True, blank=True,
        help_text="If this sighting was part of a trip, give it here. Leave blank for a non-trip sighting, e.g. just <em>knowledge</em> about the species at this place",
    )

    def __unicode__(self):
        ret = u'Sighting of %s at %s' % (self.species.common_name, self.place)
        if self.trip:
            ret += ' during trip %s' % self.trip
        return ret
