from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils import simplejson

import datetime

class ChangeRequestGroup(models.Model):
    """
    A group of ChangeRequests that cannot sensibly be applied individually.
    """

    created_at = models.DateTimeField(default=datetime.datetime.now)
    # Can be created by an anonymous user
    created_by = models.ForeignKey(
        User, null=True, blank=True, related_name='created_changerequests'
    )

    def __unicode__(self):
        return u'Change group created at %s by %s' % (
                self.created_at, self.created_by
            )

    def get_pending_changerequests(self):
        return self.changerequest_set.filter(applied_by__isnull=True)

class ChangeRequest(models.Model):
    """
    A change request is a request by an unprivelidged user to change
    something in our database. Ideally our data models should not need to
    consider this kind of user submission at all - we should use the Django
    ORM to model our domain as closely as possible. Users can then create
    change requests that say things like "attribute 'title' on Article 23
    should be changed to 'foo'" or "A new many2many relationship connecting
    User 5 with group 7 should be created" or "The many2many between user 3
    and group 6 should be deleted".

    Specific types of change request are modelled as subclasses of
    ChangeRequest - this allows each of those classes to have their own
    apply() method which carries out the actual work. This may or may not
    turn out to be a good idea...
    """
    group = models.ForeignKey(ChangeRequestGroup)

    # Track if and when this change request was applied
    applied_at = models.DateTimeField(null=True, blank=True)
    applied_by = models.ForeignKey(
        User, null=True, blank=True, related_name='applied_changerequests'
    )

    # Record the subclass used - needed for fully functional model inheritance
    subclass = models.CharField(max_length=100)

    def request_description(self):
        return 'Change request'

    def apply(self, user=None):
        self.applied_at = datetime.datetime.now()
        self.applied_by = user
        self.save()

    def save(self, *args, **kwargs):
        self.subclass = self.__class__.__name__
        return super(ChangeRequest, self).save(*args, **kwargs)

    def get_real(self):
        "Returns 'real' object of correct subclass"
        return globals()[self.subclass].objects.get(pk=self.pk)

    def conflicts(self):
        raise NotImplementedError, "ChangeRequest.conflicts() is abstract"

    def __unicode__(self):
        s = u'%s (part of %s)' % (self.request_description(), self.group)

        if self.applied_at:
            if self.applied_by:
                s += u' applied at %s by %s' % (
                    self.applied_at, self.applied_by
                )
            else:
                s += u' applied at %s' % self.applied_at
        return s

class ChangeAttributeRequest(ChangeRequest):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    attribute = models.CharField(max_length=100)

    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)

    def conflicts(self):
        obj = self.content_object
        cur_value = getattr(obj, self.attribute)

        if self.old_value != cur_value:
            # The current value of the field does not match the old value, thus
            # there is a conflict.
            return True

        return False

    def apply(self, user=None):
        obj = self.content_object
        setattr(obj, self.attribute, self.new_value)
        obj.save()
        return super(ChangeAttributeRequest, self).apply(user)

    def request_description(self):
        return u'Change "%s" from "%s" to "%s" on <%s>' % (
            self.attribute, self.old_value, self.new_value, self.content_object
        )

class CreateObjectRequest(ChangeRequest):
    content_type = models.ForeignKey(ContentType)
    attributes = models.TextField() # JSON goes here

    def apply(self, user=None):
        klass = self.content_type.model_class()
        klass.objects.create(**dict([
            (str(key), value)
            for key, value in simplejson.loads(self.attributes).items()
        ]))
        return super(CreateObjectRequest, self).apply(user)

    def conflicts(self):
        return False

    def request_description(self):
        return u'Create a %s with attributes %s' % (
            self.content_type, self.attributes
        )

class DeleteObjectRequest(ChangeRequest):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def apply(self, user=None):
        self.content_object.delete()
        return super(DeleteObjectRequest, self).apply(user)

    def conflicts(self):
        # Deletion conflicts iff the object is already deleted.
        return self.content_object is None

    def request_description(self):
        return u'Delete %s' % self.content_object
