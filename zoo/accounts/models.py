from django.db import models
from django.contrib.auth.models import User

from zoo.utils import attrproperty

class UserLevel(models.Model):
    name = models.TextField(max_length=50)

    def __unicode__(self):
        return self.name

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    user_level = models.ForeignKey(UserLevel)
    
    @models.permalink
    def get_absolute_url(self):
        raise self.user.username
        return ('accounts-profile', (), {
            'username': self.user.username
        })

    @attrproperty
    def urls(self, name):
        raise 'merry hell'
        if name == 'absolute':
            return self.get_absolute_url()

    def __unicode__(self):
        return u'%s is %s' % (self.user, self.user_level)
