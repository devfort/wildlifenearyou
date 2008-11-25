from django.db import models

class FaceArea(models.Model):
    name = models.CharField(max_length=100)
    plural = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

class FacePart(models.Model):
    area = models.ForeignKey(FaceArea, related_name = 'parts')
    description = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='faceparts')

    def __unicode__(self):
        return u'%s (%s)' % (self.description, self.area)
