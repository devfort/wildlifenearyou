import datetime

from django.db import models

from django.contrib.auth.models import User
from zoo.animals.models import Species
from zoo.photos.models import Photo

class FavouriteSpecies(models.Model):
    user = models.ForeignKey(User, related_name='favourite_species')
    species = models.ForeignKey(Species, related_name='favourited')
    when_added = models.DateTimeField(null=False, blank=False)

    class Meta:
        ordering = ['-when_added']
        unique_together = ('user', 'species')

    def save(self, force_insert=False):
        if not self.id:
            self.when_added = datetime.datetime.now()
        super(FavouriteSpecies, self).save(force_insert=force_insert)

    def __unicode__(self):
        return "%s loves %s" % (self.user.username, self.species.common_name)

    @staticmethod
    def hit_parade():
        all_favourites = FavouriteSpecies.objects.all()
        species = {}
        for f in all_favourites:
            species[f.species] = species.get(f.species, 0) + 1

        species_list = species.keys()
        for s in species_list:
            s.count = species[s]

        species_list.sort(key=lambda s: s.count, reverse=True)
        return species_list

class FavouritePhoto(models.Model):
    user = models.ForeignKey(User, related_name='favourite_photos')
    photo = models.ForeignKey(Photo, related_name='favourited')
    when_added = models.DateTimeField(null=False, blank=False)

    class Meta:
        ordering = ['-when_added']
        unique_together = ('user', 'photo')

    def save(self, force_insert=False):
        if not self.id:
            self.when_added = datetime.datetime.now()
        super(FavouritePhoto, self).save(force_insert=force_insert)

    def __unicode__(self):
        return "%s loves %s" % (self.user.username, self.photo)
