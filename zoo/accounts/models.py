from django.db import models
from django.contrib.auth.models import User

class UserLevel(models.Model):
    name = models.TextField(max_length=50)
    
    def __unicode__(self):
        return self.name

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    user_level = models.ForeignKey(UserLevel)
    
    def __unicode__(self):
        return u'%s is %s' % (self.user, self.user_level)
