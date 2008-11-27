from django.db import models
from zoo.utils import attrproperty
from zoo.models import AuditedModel
from zoo.places.models import Place

class SpeciesGroup(AuditedModel):
    name = models.CharField(max_length=255, blank=False, null=False,
        unique=True
    )

    class Meta:
        verbose_name_plural = 'species groups'

    def __unicode__(self):
        return self.name

class AbstractSpecies(models.Model):
    common_name = models.CharField(max_length=500, blank=False, null=False)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, blank=False, null=False, unique=True)
    species_group = models.ForeignKey(SpeciesGroup, blank=True, null=True)

    class Meta:
        abstract = True

    @models.permalink
    def get_absolute_url(self):
        return ('species', (), {
            'slug': self.slug
        })

    @attrproperty
    def urls(self, name):
        if name == 'absolute':
            return self.get_absolute_url()

    def __unicode__(self):
        return '%s (%s)' % (self.common_name, self.latin_name)

    def seen_at(self):
        return Place.objects.filter(sighting__species=self).distinct()

class Species(AbstractSpecies):
    latin_name = models.CharField(max_length=500, blank=False, null=False)

    def has_favourited(self, user):
        if not user.is_authenticated():
            return False
        return user.favourite_species.filter(species=self).count() != 0

    class Meta:
        verbose_name_plural = 'species'

class SuperSpecies(AbstractSpecies):
    """
    A SuperSpecies is a fictional animal with special powers, such as a 
    unicorn, Narwhal or the Django Pony.
    """
    TYPE_CHOICES = [(t, t) for t in ['imaginary', 'extinct', 'alive', 'narwhals']]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, null=False, blank=False)

    latin_name = models.CharField(max_length=500, blank=True, null=True)

    @property
    def status(self):
        return {
            'imaginary': 501,
            'extinct': 410,
            'narwhals': 200,
        }[self.type]

    @property
    def plural(self):
        name = self.common_name.lower()
        if name == 'werewolf':
            return 'werewolves'
        return '%ss' % name

    class Meta:
        verbose_name_plural = 'super species'
