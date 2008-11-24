from django.db import models
from django.contrib.auth.models import User

from zoo.utils import attrproperty
from zoo.animals.models import Species
from zoo.trips.models import TripSighting

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    
    @models.permalink
    def get_absolute_url(self):
        return ('accounts-profile', (), {
            'username': self.user.username
        })

    @attrproperty
    def urls(self, name):
        if name == 'absolute':
            return self.get_absolute_url()

    def __unicode__(self):
        return u'Profile for %s' % (self.user)

    # the user's animal passport
    def passport(self):
        class Passport:
            def __init__(self, seen):
                self.seen_species = seen

        species_list = list(Species.objects.filter(trip__user=self.user))
        by_count = {}
        for species in species_list:
            by_count[species] = by_count.get(species, 0) + 1
            
        species_list = by_count.keys()
        
        for species in species_list:
            species.count = by_count[species]

        species_list.sort(key=lambda s:s.count, reverse=True)
        
        o = Passport(species_list)
        return o
