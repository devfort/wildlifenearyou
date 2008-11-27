from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType


import datetime
from itertools import chain

from zoo.fields import JSONField

def get_pretty_field_key(val):
    if val.endswith('_id'):
        val = val[:-3]
    return val.replace('_', ' ').capitalize()

def get_pretty_field_value(val, instance, attribute):
    if not attribute.endswith('_id'):
        return val

    klass = instance.content_type.model_class()
    dummy_obj = klass()
    setattr(dummy_obj, attribute, val)
    return getattr(dummy_obj, attribute[:-3])

def reformat_foreign_keys(fn):
    def wrapper(self, *args, **kwargs):
        val = fn(self, *args, **kwargs)
        return get_pretty_field_value(val, self, self.attribute)
    return wrapper

class ChangeRequestGroup(models.Model):
    """
    A group of ChangeRequests that cannot sensibly be applied individually.
    """

    created_at = models.DateTimeField(default=datetime.datetime.now)
    # Can be created by an anonymous user
    created_by = models.ForeignKey(
        User, null=True, blank=True, related_name='created_changerequests'
    )

    class Meta:
        ordering = ['-created_at']

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
        return None

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

    def save(self, *args, **kwargs):
        def pkify(obj):
            if isinstance(obj, models.Model):
                return obj.pk
            else:
                return obj

        self.old_value = pkify(self.old_value)
        self.new_value = pkify(self.new_value)

        super(ChangeAttributeRequest, self).save(*args, **kwargs)

    def conflicts(self):
        # The current value of the field does not match the old value, thus
        # there is a conflict.
        return self.old_value != getattr(self.content_object, self.attribute)

    @reformat_foreign_keys
    def get_current_value_display(self):
        return getattr(self.content_object, self.attribute)

    @reformat_foreign_keys
    def get_old_value_display(self):
        return self.old_value

    @reformat_foreign_keys
    def get_new_value_display(self):
        return self.new_value

    def get_attribute_display(self):
        return get_pretty_field_key(self.attribute)

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
    parent = models.ForeignKey('self', null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    attributes = JSONField()
    reverse_relation = models.TextField()

    def children(self):
        return self.__class__.objects.filter(parent=self)

    def apply(self, user=None):
        klass = self.content_type.model_class()
        instance = klass(**self.attributes)

        if hasattr(instance, 'slug') and hasattr(instance, 'get_slug_suggestions'):
            def get_slug():
                slug = ""

                # Get slug suggestions from model
                for suggestion in instance.get_slug_suggestions():
                    # Don't append blank strings, None etc.
                    if not suggestion:
                        continue

                    if slug:
                        slug += "-"

                    slug += slugify(suggestion)
                    if klass.objects.filter(slug=slug).count() == 0:
                        return slug

                if slug:
                    slug += "-"

                for i in range(2, 1000):
                    num_slug = "%s%d" % (slug, i)
                    if klass.objects.filter(slug=num_slug).count() == 0:
                        return num_slug

                assert False, "Slug suggestions exhuasted"
            instance.slug = get_slug()

        instance.save()
        super(CreateObjectRequest, self).apply(user)
        return instance

    def get_attributes_display(self):
        return dict([
            (get_pretty_field_key(k), get_pretty_field_value(v, self, k))
            for k, v in self.attributes.iteritems()])

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
