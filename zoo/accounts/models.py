import datetime
import md5

from django.conf import settings

from django.db import models
from django.contrib.auth.models import User
from django.template import loader, Context
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment
from django.utils.safestring import mark_safe

import zoo.utils
from zoo.utils import attrproperty
from zoo.utils import make_absolute_url as absurl
from zoo.trips.models import Trip, Sighting
from zoo.animals.models import Species
from zoo.common.models import AuditedModel
from zoo.favourites.models import FavouriteSpecies
from zoo.faces.models import SelectedFacePart
from zoo.photos.models import Photo

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
    biography = models.TextField(null=False, blank=True)
    url = models.URLField(null=False, blank=True, verify_exists=False)
    percentage_complete = models.IntegerField(null=False, blank=False, default=0) # see recalculate_percentage_complete()

    email_validated = models.BooleanField(null=False, blank=False, default=False)
    featured = models.BooleanField(null=False, blank=False, default=False)
    
    # Three fields for location: the first is a text description
    location = models.TextField(max_length=100, blank=True)
    # The other two are lat and lon
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Searchable:
        fields = [
            { # Searching for people by name.
                'field_name': 'name',
                'django_fields': [lambda x: [x.user.username], lambda x: [x.user.get_full_name()]],
                'config': {'store': True, 'freetext': {'language': 'en'}},
            }, { # Searching by biography.
                'field_name': 'biography',
                'django_fields': ['biography'],
                'config': {'store': True, 'freetext': {'language': 'en'}},
            }, { # Location of the person.
                'field_name': 'latlon',
                'django_fields': [lambda inst: [inst.latlon()]],
                'config': {'type': 'geo', 'geo': {}, 'store': True}
            },
        ]
        xapian_index = 'userinfo'

    def latlon(self):
        if self.longitude is None or self.latitude is None:
            return ''
        return "%f %f" % (self.latitude, self.longitude)

    def points_image(self):
        """The PNG within /static/img/engagementbadge/ ."""
        return 'monkey'
        
    def points_animal(self):
        """Which animal are we, based on animal points? (currently still stored as percentage_complete)"""
        return 'helpful macaque'

    def avatar_img(self):
        return mark_safe(
            '<img src="%s" class="avatar" alt="%s\'s Avatar" width="175" height="175">' % (
                self.face_large(),
                self.user.username
            )
        )

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
    
    def face(self, size):
        key, keydir = self.get_face_key_and_keydir()
        return '/static/uploaded/faces/%s/%s-%s.png' % (
            keydir, key, size
        )
    
    def face_small(self):
        return self.face('small')
    
    def face_medium(self):
        return self.face('medium')
    
    def face_large(self):
        return self.face('large')
    
    def get_face_key_and_keydir(self):
        parts = [
            s.part 
            for s in self.user.selectedfaceparts.all().select_related('part')
        ]
        if parts:
            key = '-'.join([str(part.pk) for part in parts])
            # e.g. '623-485-548-566-590-600-583'
        else:
            key = 'default'
        if '-' in key:
            keydir = '-'.join(key.split('-')[:2]) # e.g. '623-485'
        else:
            keydir = 'default'
        
        return key, keydir
    
    def visible_photos(self):
        return self.user.photos.filter(is_visible=True)

    def passport(self):
        return Trip.get_passport(self.user)

    def _generate_user_hash(self, username):
        days = int_to_hex((datetime.date.today() - HASH_ORIGIN_DATE).days)
        hash = md5.new(settings.SECRET_KEY + days + username).hexdigest()
        return (hash, days)

    def send_email(self, subject, template, kwargs, to_email=None):
        body = render_to_string(template, kwargs)
        if to_email is None:
            to_email = self.user.email

        import smtplib
        try:
            zoo.utils.send_mail(
                subject, body,
                settings.EMAIL_FROM, [to_email],
                fail_silently=False
            )
        except smtplib.SMTPException:
            # TODO: handle failed email sending
            pass

    def send_validation_email(self):
        self.send_email('Validation required',
                        'emails/validation.txt',
                        {'user': self.user,
                         'url': self.email_validation_url_for_user()
                         })
    send_validation_email.alters_data = True

    def send_invitation_email(self, to_name, to_email, ref=None):
        """Send an email inviting a friend to check out WildlifeNearYou. If ref set, highlights a particular page."""
        self.send_email('Check out WildlifeNearYou!',
                        'emails/invite.txt',
                        {'user': self.user,
                         'to_name': to_name,
                         'to_email': to_email,
                         'url': absurl(reverse('homepage')),
                         'link': absurl(ref),
                         },
                         to_email)
    send_invitation_email.alters_data = True

    def send_password_key_email(self):
        self.send_email('You can change your password',
                        'emails/password_key.txt',
                        {'user': self.user,
                         'url': self.password_key_url_for_user()
                         })
    send_password_key_email.alters_data = True

    def send_welcome_email(self):
        from django.contrib.sites.models import Site
        site = Site.objects.all()[0] # there can be only one.
        self.send_email('Welcome to Narwhals.com!',
                        'emails/welcome.txt',
                        {'user': self.user,
                         'site': site,
                         'site_email': 'us@example.com',
                         })
    send_welcome_email.alters_data = True

    def email_validation_url_for_user(self):
        (hash, days) = self._generate_user_hash(self.user.username)
        return absurl(
            reverse(
                'validate-email',
                args=(self.user.username.lower(), days, hash,)
            )
        )

    def password_key_url_for_user(self):
        (hash, days) = self._generate_user_hash(self.user.username)
        return absurl(
            reverse(
                'recover-password',
                args=(self.user.username.lower(), days, hash,)
            )
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

    # This works by having a postsave hook (below) that calls this on certain save actions.
    def recalculate_percentage_complete(self):
        self.percentage_complete = self._percentage_complete()
        qs = Profile.objects.filter(pk=self.pk)
        qs.update(percentage_complete = self.percentage_complete)

    # If you add something new in here that means more model saves need to be checked, don't forget to
    # update the hook (below).
    def _percentage_complete(self):
        percent = 0
        if self.biography: percent += 10
        if self.user.get_full_name(): percent += 10
        if self.url: percent += 5
        if self.latitude!=None and self.longitude!=None: percent += 15
        if self.user.created_sighting_set.count() > 0: percent += 5
        if self.user.photos.filter(is_visible=True).count() > 0: percent += 5
        if self.user.comment_comments.all().count() > 0: percent += 5
        photo_ids = self.user.photos.values_list('id', flat=True)
        pct = ContentType.objects.get_for_model(Photo)
        # Note that if things get slow, it's probably the following not optimising properly as the number of photos
        # increases.
        if Comment.objects.filter(content_type = pct, object_pk__in = photo_ids).exclude(user = self.user).count() > 0:
            percent += 5
        if self.user.selectedfaceparts.count() > 0: percent += 10 # avatar / profile picture
        if self.user.favourite_species.all().count() > 0: percent += 5
        if self.user.created_sighting_set.count() > 10: percent += 5
        if self.user.photos.filter(is_visible=True).count() > 10: percent += 5
        if self.user.created_sighting_set.count() > 100: percent += 5
        if self.user.photos.filter(is_visible=True).count() > 100: percent += 5
        # 5% reserved. Once we fill that up, we'll start awarding badges for specific things instead.

        return percent

# Ensure that when a User object is saved, we save the profile as well (if any).
# This guarantees correct reindexing. We can't do it the normal way (by shoving a
# searchable class within the User model) because that's monkeypatching and somewhat
# grotty.
#
# Ideally we should wrap this mechanism into a reverse cascades system in Searchify.
from django.db.models.signals import post_save
def autosave_profile(sender, **kwargs):
    profiles = Profile.objects.filter(user=kwargs['instance'])
    if len(profiles)==1:
        profiles[0].save()
post_save.connect(autosave_profile, User)

# presave hook to update profile percentage completion
def profilecalc_postsave(sender, **kwargs):
    instance = kwargs['instance']
    user = None
    if sender==Profile:
        instance.recalculate_percentage_complete()
        return
    elif sender==User: # FIXME: not picked up (we're forcing it for now in the edit profile view)
        user = instance
    elif sender==Sighting:
        user = instance.created_by
    elif sender==Photo:
        user = instance.created_by
    elif sender==Comment:
        user = instance.user
    elif sender==FavouriteSpecies:
        user = instance.user
    elif sender==SelectedFacePart:
        user = instance.user
    if user:
        try:
            profile = user.get_profile()
            profile.recalculate_percentage_complete()
        except:
            # not ready for us yet
            pass
