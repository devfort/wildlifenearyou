from django.db import models

class RspbBirdPage(models.Model):
    name = models.CharField(max_length = 255)
    species = models.ManyToManyField(
        'animals.Species', blank = True, null = True
    )
    url = models.URLField(max_length = 255, verify_exists = False)
    image_url = models.CharField(max_length = 255, blank = True)
    teaser = models.TextField(blank = True)
    
    def __unicode__(self):
        return self.name
