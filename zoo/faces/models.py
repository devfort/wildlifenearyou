from django.db import models
from django.contrib.auth.models import User

class FaceAreaCategory(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField(blank = True, null=True, help_text="""
        This is the order the tabs show up in the SWF
    """.strip())
    is_special = models.BooleanField(help_text = """
        Special categories are not available to everyone - users can have them
        enabled for their account (e.g. zoo keepers hats)
    """.strip())
    
    class Meta:
        verbose_name_plural = 'face area categories'
        ordering = ('order',)
    
    def __unicode__(self):
        if self.is_special:
            return u'%s (special)' % self.name
        else:
            return self.name

class FaceAreaManager(models.Manager):
    def for_user(self, user_or_username):
        if isinstance(user_or_username, basestring):
            user = User.objects.get(username = user_or_username)
        else:
            user = user_or_username
        return (
            list(self.filter(category__is_special = False)) + 
            list(self.filter(
                category__is_special = True,
                category__specialperms__user = user
            ))
        )

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
    
    objects = FaceAreaManager()
    
    class Meta:
        ordering = ('order',)
    
    def __unicode__(self):
        return self.name

class FacePart(models.Model):
    area = models.ForeignKey(FaceArea, related_name = 'parts')
    description = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='faceparts')

    def __unicode__(self):
        return self.description

class SelectedFacePart(models.Model):
    part = models.ForeignKey(FacePart)
    area = models.ForeignKey(FaceArea)
    user = models.ForeignKey('auth.User', related_name='selectedfaceparts')
    
    class Meta:
        unique_together = ('area', 'user')
        ordering = ('area__order',)
    
    def __unicode__(self):
        return u'%s picked %s for area %s' % (
            self.user, self.part, self.area
        )

class SpecialPermission(models.Model):
    category = models.ForeignKey(
        FaceAreaCategory, related_name='specialperms'
    )
    user = models.ForeignKey('auth.User')
    
    def __unicode__(self):
        return u'%s can use %s' % (self.user, self.category)
