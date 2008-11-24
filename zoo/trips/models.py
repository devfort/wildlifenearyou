from django.db import models
import datetime

from django.contrib.auth.models import User
from zoo.places.models import Place
from zoo.animals.models import Species
from zoo.utils import attrproperty

class Trip(models.Model):
    start = models.DateTimeField(null=False, blank=False)
    end = models.DateTimeField(null=False, blank=True)
    place = models.ForeignKey(Place)
    user = models.ForeignKey(User, related_name='trips')
    name = models.CharField(null=True, blank=True, max_length=100)
    sightings = models.ManyToManyField(Species, through='TripSighting')
    
    def save(self, *args, **kwargs):
        if self.end==None:
            self.end = self.start + datetime.timedelta(1)
        super(Trip,self).save(args, kwargs)
    
    #THIS MUST BE static.  It does not act on an instance and is called from the profile model
    @staticmethod
    def get_passport(user):
        class Passport:
            def __init__(self, seen):
                self.seen_species = seen
        
        species_list = list(Species.objects.filter(trip__user=user))
        by_count = {}
        for species in species_list:
            by_count[species] = by_count.get(species, 0) + 1

        species_list = by_count.keys()

        for species in species_list:
            species.count = by_count[species]

        species_list.sort(key=lambda s:s.count, reverse=True)

        o = Passport(species_list)
        return o
        
    def title(self):
        if self.name:
            return self
        else:
            #FIX ME - Need I18N
            return u'your trip to %s' % (self.place.known_as)
        
    def __unicode__(self):
        return self.user.username + u'@' + self.place.known_as

class TripSighting(models.Model):
    trip = models.ForeignKey(Trip)
    species = models.ForeignKey(Species)
    
    def __unicode__(self):
        return u'' + unicode(self.trip) + u': ' + self.species.common_name
