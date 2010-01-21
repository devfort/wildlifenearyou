from django.db import models
from zoo.common.models import AuditedModel

class List(AuditedModel):
    title = models.CharField(max_length = 255)
    slug = models.SlugField()
    description = models.TextField(blank = True)
    source_url = models.URLField(
        max_length = 255, verify_exists = False, blank = True
    )
    species = models.ManyToManyField('animals.Species', blank=True, null=True)
    places = models.ManyToManyField('places.Place', blank=True, null=True)
    
    def __unicode__(self):
        return self.title
