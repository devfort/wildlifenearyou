from django.db import models

class FaceArea(models.Model):
    name = models.CharField(max_length=100)
    plural = models.CharField(max_length=100)
    shortname = models.SlugField(max_length=30)
    
    def __unicode__(self):
        return self.name
    
class FacePart(models.Model):
    area = models.ForeignKey(FaceArea, related_name = 'parts')
    description = models.CharField(max_length=100)
    image = models.ImageField(upload_to='faceparts')
    
    def __unicode__(self):
        return u'%s (%s)' % (self.description, self.area)
