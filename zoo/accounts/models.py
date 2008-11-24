from django.db import models
from django.contrib.auth.models import User

from zoo.utils import attrproperty

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    
    @models.permalink
    def get_absolute_url(self):
        return ('accounts-profile', (), {
            'username': self.user.username
        })

    @attrproperty
    def urls(self, name):
        if name == 'absolute':
            return self.get_absolute_url()

    def __unicode__(self):
        return u'Profile for %s' % (self.user)
