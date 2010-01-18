from django.db import models
from zoo.places.models import Place

class PlaceNeedsCleanup(models.Model):
    place = models.ForeignKey(Place)
    
    def __unicode__(self):
        return u'Cleanup: %s' % self.place

def create_for_all_places():
    for place in Place.objects.all():
        PlaceNeedsCleanup.objects.create(place = place)
