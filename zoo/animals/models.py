from django.db import models
from zoo.utils import attrproperty
from zoo.models import AuditedModel

class SpeciesGroup(AuditedModel):
    name = models.CharField(max_length=255, blank=False, null=False,
        unique=True
    )

    class Meta:
        verbose_name_plural = 'species groups'

    def __unicode__(self):
        return self.name

class Species(AuditedModel):
    common_name = models.CharField(max_length=500, blank=False, null=False)
    latin_name = models.CharField(max_length=500, blank=False, null=False)
    slug = models.SlugField(max_length=255, blank=False, null=False, unique=True)
    species_group = models.ForeignKey(SpeciesGroup)

    class Meta:
        verbose_name_plural = 'species'

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
        return '%s (%s)' % (self.common_name, self.latin_name,)

