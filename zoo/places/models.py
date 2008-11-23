import datetime

from django.db import models

from zoo.animals.models import Animal

class Country(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    country_code = models.CharField(max_length=2, null=False, blank=False, unique=True)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.country_code,)

class Place(models.Model):
    legal_name = models.CharField(max_length=500, null=False, blank=False)
    known_as = models.CharField(max_length=500, null=False, blank=False)
    slug = models.SlugField(max_length=255, null=False, blank=False, unique=True)
    created_at = models.DateTimeField(null=False, blank=False)
    last_modified_at = models.DateTimeField(null=False, blank=False)

    def save(self):
        if not self.id:
            self.created_at = datetime.datetime.now()
        self.last_modified_at = datetime.datetime.now()
        super(Place, self).save()

    # Address
    address_line_1 = models.CharField(max_length=250, null=True, blank=True)
    address_line_2 = models.CharField(max_length=250,  null=True, blank=True)
    town = models.CharField(max_length=250, null=True, blank=True)
    state = models.CharField(max_length=250, null=True, blank=True)
    zip = models.CharField(max_length=50, null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    
    def address(self):
        bits = []
        for attr in (
            'address_line_1', 'address_line_2', 'town', 'state', 'zip',
            'country'
            ):
            val = unicode(getattr(self, attr, None))
            if val:
                bits.append(val)
        return '\n'.join(bits)
    
    # long and lot for mapping
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return '%s, commonly known as %s' % (self.legal_name, self.known_as,)

class Enclosure(models.Model):
    place = models.ForeignKey(Place, related_name = 'enclosures')
    animals = models.ManyToManyField(Animal, through='EnclosureAnimal')
    name = models.CharField(max_length=300, null=True, blank=True)

    def __unicode__(self):
        return self.name

class EnclosureAnimal(models.Model):
    enclosure = models.ForeignKey(Enclosure)
    animal = models.ForeignKey(Animal)
    number_of_inhabitants = models.IntegerField(default=0, null=True, blank=True)
