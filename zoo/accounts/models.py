import datetime
import md5

from django.conf import settings

from django.db import models
from django.contrib.auth.models import User
from django.template import loader, Context
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

import zoo.utils
from zoo.utils import attrproperty
from zoo.trips.models import Trip
from zoo.animals.models import Species
from zoo.models import AuditedModel

HASH_ORIGIN_DATE = datetime.date(2000, 1, 1)

hex_to_int = lambda s: int(s, 16)
int_to_hex = lambda i: hex(i).replace('0x', '')

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

    email_validated = models.BooleanField(null=False, blank=False, default=False)

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

    def _generate_user_hash(self, username):
        days = int_to_hex((datetime.date.today() - HASH_ORIGIN_DATE).days)
        hash = md5.new(settings.SECRET_KEY + days + username).hexdigest()
        return (hash, days)

    def send_validation_email(self):
        body = render_to_string('emails/validation.txt',
                                {'user': self.user,
                                 'url': self.email_validation_url_for_user()
                                 })

        import smtplib
        try:
            zoo.utils.send_mail(
                'Welcome to BLAH', body,
                settings.EMAIL_FROM, [self.user.email],
                fail_silently=False
            )
        except smtplib.SMTPException:
            # TODO: handle failed email sending
            pass

    send_validation_email.alters_data = True

    def email_validation_url_for_user(self):
        (hash, days) = self._generate_user_hash(self.user.username)
        return reverse('validate-email',
                       args=(self.user.username, days, hash,)
                       )

    def hash_is_valid(self, days, hash):
        if md5.new(settings.SECRET_KEY + days + self.user.username).hexdigest() != hash:
            return False # Hash failed
        # Ensure days is within a week of today
        days_now = (datetime.date.today() - HASH_ORIGIN_DATE).days
        days_old = days_now - hex_to_int(days)
        if days_old < 7:
            return True
        else:
            return False

    def is_not_brand_new_account(self):
        return self.user.date_joined < (
            datetime.datetime.now() - datetime.timedelta(days = 7)
        )
