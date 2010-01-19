from django.db import models

class Gimmick(models.Model):
    domain = models.CharField(
        max_length=100, help_text='e.g. ottersnearyou.com'
    )
    singlular = models.CharField(max_length=40, help_text = 'e.g. otter')
    plural = models.CharField(max_length=40, help_text = 'e.g. otters')
    species = models.ManyToManyField('animals.Species',
        help_text = 'Pick the actual species to be included'
    )
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    custom_template = models.TextField(blank = True)
    google_analytics = models.TextField(blank = True, null = True)
    
    def __unicode__(self):
        return self.domain
