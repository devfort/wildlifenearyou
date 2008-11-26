from django.db import models
from django.contrib.auth.models import User

from zoo.utils import attrproperty
from zoo.trips.models import Trip
from zoo.animals.models import Species

import datetime

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)

    @models.permalink
    def get_absolute_url(self):
        return ('accounts-profile', (), {
            'username': self.user.username,
        })

    @attrproperty
    def urls(self, name):
        if name == 'absolute':
            return self.get_absolute_url()

    def __unicode__(self):
        return u'Profile for %s' % (self.user,)

    def passport(self):
        return Trip.get_passport(self.user)
    
    def is_not_brand_new_account(self):
        return self.user.date_joined < (
            datetime.datetime.now() - datetime.timedelta(days = 7)
        )
