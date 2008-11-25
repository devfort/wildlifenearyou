from django.db import models
import datetime

from django.contrib.auth.models import User
from zoo.animals.models import Species
from zoo.utils import attrproperty
from zoo.models import AuditedModel
#from zoo.places.models import Place

class Trip(AuditedModel):
    start = models.DateTimeField(null=False, blank=True)
    end = models.DateTimeField(null=False, blank=True)
    name = models.CharField(null=True, blank=True, max_length=100)
    sightings = models.ManyToManyField(Species, through='Sighting')

    class Meta:
        ordering = ['-start']

    def save(self, *args, **kwargs):
        if self.end==None:
            self.end = self.start + datetime.timedelta(1)
        super(Trip,self).save(args, kwargs)

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

        o = Passport(species_list)
        return o
        
    def title(self):
        if self.name:
            return self

        # FIXME - Need I18N
        return u'your trip to %s' % (self.place.known_as)

    def __unicode__(self):
        return self.created_by.username + u', ' + self.name

class Sighting(AuditedModel):
    place = models.ForeignKey('places.Place')
    species = models.ForeignKey(Species)
    trip = models.ForeignKey(Trip, null=True, blank=True)

    def __unicode__(self):
        str = 'Sighting of ' + self.species.common_name + ' at ' + unicode(self.place)
        if self.trip:
            str += ' during trip ' + unicode(self.trip)
        return str
