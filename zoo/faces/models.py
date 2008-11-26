from django.db import models

class FaceAreaCategory(models.Model):
    name = models.CharField(max_length=100)
    is_special = models.BooleanField(help_text = """
        Special categories are not available to everyone - users can have them
        enabled for their account (e.g. zoo keepers hats)
    """.strip())
    
    class Meta:
        verbose_name_plural = 'face area categories'
    
    def __unicode__(self):
        if self.is_special:
            return u'%s (special)' % self.name
        else:
            return self.name

class FaceArea(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.IntegerField(blank = True, null=True, help_text="""
        Order is needed to ensure that the images are stacked correctly on 
        top of each other
    """.strip())
    category = models.ForeignKey(
        FaceAreaCategory, blank=True, null=True, related_name = 'areas'
    )
    
    class Meta:
        ordering = ('order',)
    
    def __unicode__(self):
        return self.name

class FacePart(models.Model):
    area = models.ForeignKey(FaceArea, related_name = 'parts')
    description = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='faceparts')

    def __unicode__(self):
        return u'%s (%s)' % (self.description, self.area)

class SpecialPermission(models.Model):
    category = models.ForeignKey(FaceAreaCategory)
    user = models.ForeignKey('auth.User')
    
    def __unicode__(self):
        return u'%s can use %s' % (self.user, self.category)
