from django.db import models
from zoo.utils import attrproperty
from zoo.common.models import AuditedModel
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

    @models.permalink
    def get_spotters_url(self):
        return ('species-spotters', (), {
            'slug': self.slug
        })

    @attrproperty
    def urls(self, name):
        if name == 'absolute':
            return self.get_absolute_url()
        if name == 'spotters':
            return self.get_spotters_url()

    def article(self):
        if self.common_name[0] in ('a','e','i','o','u','A','E','I','O','U'):
            return 'an'
        return 'a'

    def __unicode__(self):
        return '%s (%s)' % (self.common_name, self.latin_name)

    def seen_at(self):
        return Place.objects.filter(sighting__species=self).distinct()

class Species(AbstractSpecies):
    latin_name = models.CharField(max_length=500, blank=False, null=False)
    freebase_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    featured = models.BooleanField(null=False, blank=False, default=False)
    plural_override = models.CharField(max_length=500, blank=True, null=True,
        help_text = (
            "If the plural of this animal is more complicated than "
            "just adding an 's' on the end, provide it here e.g. Sheep"
        )
    )
    
    def plural(self):
        return self.plural_override or (self.common_name + 's')
    
    def visible_photos(self):
        from zoo.photos.models import Photo
        return Photo.objects.filter(
            sightings__species = self, is_visible = True,
        ).distinct()

    def photo(self):
        if self.visible_photos().count() >= 1:
            return self.random_photo()
        else:
            # Here is where to return a picture of some trees
            # (it would perhaps be nice to have a variety of different photos available)
            return None

    def random_photo(self):
        vp = self.visible_photos()
        if vp.count():
            return vp.order_by('?')[0]
        return None

    def has_favourited(self, user):
        if not user.is_authenticated():
            return False
        return user.favourite_species.filter(species=self).count() != 0

    def popularity(self):
        """
        Currently just calculated using number of sightings of this
        species.
        """

        num_of_sightings = float(self.sightings.all().count())

        return 1 - (1 / (num_of_sightings + 1))

    class Meta:
        verbose_name_plural = 'species'

    class Searchable:
        fields = [
            { # Searching for species by name.
                'field_name': 'common_name',
                'django_fields': ['common_name'],
                'config': {
                    'store': True,
                    'freetext': {'language': 'en'}
                },
            }, { # Searching for the place address.
                'field_name': 'latin_name',
                'django_fields': ['latin_name'],
                'config': {'store': True},
            }, { # Searching for the place address.
                'field_name': 'description',
                'django_fields': ['description'],
                'config': {'freetext': {'language': 'en'}},
            }
            # TODO: Index places you can see this animal perhaps?
        ]
        xapian_index = 'known_species'

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
