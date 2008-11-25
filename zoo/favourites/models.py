import datetime

from django.db import models

from django.contrib.auth.models import User
from zoo.animals.models import Species

class FavouriteSpecies(models.Model):
    user = models.ForeignKey(User, related_name='favourite_species')
    species = models.ForeignKey(Species)
    when_added = models.DateTimeField(null=False, blank=False)

    class Meta:
        ordering = ['-when_added']
        unique_together = ('user', 'species')

    def save(self, force_insert=False):
        if not self.id:
            self.when_added = datetime.datetime.now()
        super(FavouriteSpecies, self).save(force_insert=force_insert)

    def __unicode__(self):
        return "%s loves %s" % (self.user.username, self.species.common_name,)
