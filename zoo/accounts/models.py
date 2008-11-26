from django.db import models
from django.contrib.auth.models import User

from zoo.utils import attrproperty
from zoo.trips.models import Trip
from zoo.animals.models import Species
from zoo.models import AuditedModel

class Badge(models.Model):
    name = models.CharField(null=False, blank=False, max_length=100)
    
    def __unicode__(self):
        return self.name

class ProfileBadge(AuditedModel):
    profile = models.ForeignKey('Profile')
    badge = models.ForeignKey(Badge)
    
    def __unicode__(self):
        return u'%s: %s' % (unicode(self.profile.user), unicode(self.badge),)

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    badges = models.ManyToManyField(Badge, through=ProfileBadge)

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
