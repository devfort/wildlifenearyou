from django.db import models
from django.contrib.auth.models import User

import datetime

from zoo.utils import attrproperty
from zoo.models import AuditedModel
from zoo.animals.models import Species

class Trip(AuditedModel):
    start = models.DateTimeField(null=False, blank=True)
    end = models.DateTimeField(null=False, blank=True)
    name = models.CharField(null=True, blank=True, max_length=100)
    description = models.TextField(blank=True)
    sightings = models.ManyToManyField(Species, through='Sighting')

    class Meta:
        ordering = ['-start']

    def save(self, *args, **kwargs):
        if self.end is None and self.start:
            self.end = self.start + datetime.timedelta(1)
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

    def title(self):
        if self.name:
            return self

        # FIXME - Need I18N
        return u'your trip to %s' % self.place.known_as

    def __unicode__(self):
        return u"%s, %s" % (self.created_by.username, self.name)

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
