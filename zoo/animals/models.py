from django.db import models
from django.db.models import Count
from zoo.utils import attrproperty
from zoo.common.models import AuditedModel
from zoo.places.models import Place
from zoo.shorturl.utils import converter

from django.core.cache import cache
from redis_db import r

import urllib, re
from django.utils import simplejson

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
        if self.latin_name:
            return '%s (%s)' % (self.common_name, self.latin_name)
        else:
            return self.common_name
    
    def seen_at(self):
        places = list(Place.objects.filter(
            sighting__species = self,
            is_unlisted = False,
        ).distinct())
        for place in places:
            photos_of_self = place.visible_photos().filter(
                sightings__species = self
            )
            if photos_of_self:
                place.photo_of_species = photos_of_self[0]
            else:
                place.photo_of_species = None
        return places

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
    needs_indexing = models.BooleanField(default = True)
    
    def plural(self):
        return self.plural_override or (self.common_name + 's')
    
    def visible_photos(self):
        from zoo.photos.models import Photo
        return Photo.objects.filter(
            sightings__species = self, is_visible = True,
        ).select_related('created_by').distinct()

    def photo(self):
        photo = cache.get('photo-of-species:%s' % self.pk)
        if photo is None:
            best = r.zrange('bestpics-species:%s' % self.pk, 0, 0, desc=True)
            if best:
                from zoo.photos.models import Photo
                try:
                    photo = Photo.objects.get(pk = best[0])
                except Photo.DoesNotExist:
                    photo = 'no-photo'
            else:
                try:
                    photo = self.visible_photos().annotate(
                        num_faves = Count('favourited')
                    ).select_related('created_by').order_by('-num_faves')[0]
                except IndexError:
                    photo = 'no-photo'
            cache.set('photo-of-species:%s' % self.pk, photo, 60 * 60 * 5)
        
        if photo == 'no-photo':
            return None
        return photo
    
    def top_3_photo_ids(self):
        return r.zrange('bestpics-species:%s' % self.pk, 0, 2, desc=True)
    
    def random_photo(self):
        vp = self.visible_photos()
        if vp.count():
            return vp.order_by('?')[0]
        return None

    def is_favourited_by(self, user):
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
    
    def wikipedia_page(self):
        ids = list(self.external_identifiers.filter(
            namespace = '/wikipedia/en'
        ).order_by('order')[:1])
        r = re.compile('\$\d{4}')
        if ids:
            key = ids[0].key
            # Deal with weird $0027 -style escaping scheme
            key = r.sub(lambda m: unichr(int(m.group(0)[1:], 16)), key)
            encoded_key = urllib.urlencode({'q': key}).replace('q=', '')
            url = 'http://en.wikipedia.org/wiki/%s' % encoded_key
            title = key.replace('_', ' ')
            return url, title
        else:
            return None, None
    
    def bbc_wildlifefinder_url(self):
        ids = list(self.external_identifiers.filter(
            namespace = '/user/pak21/bbcnathist/bbc_id'
        ).order_by('order')[:1])
        if ids:
            return 'http://www.bbc.co.uk/nature/species/%s' % ids[0].key
        else:
            return None
    
    def update_external_identifiers(self):
        url = "http://ids.freebaseapps.com/get_ids?id=%s" % self.freebase_id
        json = simplejson.load(urllib.urlopen(url))
        for i, link in enumerate(json['ids']):
            self.external_identifiers.get_or_create(
                source = link['source'],
                namespace = link['namespace'],
                key = link['key'],
                defaults = {
                    'uri': link['uri'],
                    'order': i,
                }
            )
        return json['ids']
    
    def short_code(self):
        return 's%s' % converter.from_int(self.pk)
    
    def short_url(self):
        return 'http://wlny.eu/%s' % self.short_code()
    
    def has_flickr_tagged_photos(self):
        from flickr.models import FlickrTagsApplied
        return bool(
            FlickrTagsApplied.objects.filter(
                photo__sightings__species = self
            ).extra(select={'a': 1}).values('a').order_by()[:1]
        )
    
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
            }, { # Latin name.
                'field_name': 'latin_name',
                'django_fields': ['latin_name'],
                'config': {'store': True},
            }, { # Description of species.
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
