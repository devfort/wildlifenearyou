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
    user = models.ForeignKey(User)
    name = models.CharField(null=True, blank=True, max_length=100)
    sightings = models.ManyToManyField(Species, through='TripSighting')
    
    def save(self, *args, **kwargs):
        if self.end==None:
            self.end = self.start + datetime.timedelta(1)
        super(Trip,self).save(args, kwargs)

    def __unicode__(self):
        return self.user.username + u'@' + self.place.known_as

class TripSighting(models.Model):
    trip = models.ForeignKey(Trip)
    species = models.ForeignKey(Species)

    def __unicode__(self):
        return u'' + unicode(self.trip) + u': ' + self.species.common_name
