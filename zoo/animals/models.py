from django.db import models
from zoo.utils import attrproperty

class AnimalClass(models.Model):
    name = models.CharField(max_length=500, blank=False, null=False)

    def __unicode__(self):
        return self.name

class Animal(models.Model):
    common_name = models.CharField(max_length=500, blank=False, null=False)
    latin_name = models.CharField(max_length=500, blank=False, null=False)
    animal_class = models.ForeignKey(AnimalClass)

    @models.permalink
    def get_absolute_url(self):
        return ('animal', (), {'common_name': self.common_name})

    @attrproperty
    def urls(self, name):
        if name == 'absolute':
            return self.get_absolute_url()

    def __unicode__(self):
        return '%s (%s) of class %s' % (self.common_name, self.latin_name, self.animal_class.name,)
    
