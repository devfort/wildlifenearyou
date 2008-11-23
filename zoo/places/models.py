import datetime

from django.db import models

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

    def __unicode__(self):
        return '%s, commonly known as %s' % (self.legal_name, self.known_as,)
