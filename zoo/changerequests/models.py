from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils import simplejson

import datetime

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
    created_at = models.DateTimeField(default=datetime.datetime.now)
    # Can be created by an anonymous user
    created_by = models.ForeignKey(
        User, null=True, blank=True, related_name = 'created_changerequests'
    )
    # Track if and when this change request was applied
    applied_at = models.DateTimeField(null=True, blank=True)
    applied_by = models.ForeignKey(
        User, null=True, blank=True, related_name = 'applied_changerequests'
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
        super(ChangeRequest, self).save(*args, **kwargs)
    
    def get_real(self):
        "Returns 'real' object of correct subclass"
        return globals()[self.subclass].objects.get(pk = self.pk)
    
    def __unicode__(self):
        if self.created_by:
            s = u'%s created at %s by %s' % (
                self.request_description(), self.created_at, self.created_by
            )
        else:
            s = u'%s created at %s' % (
                self.request_description(), self.created_at
            )
        if self.applied_at:
            if self.applied_by:
                s += u' (applied at %s by %s)' % (
                    self.applied_at, self.applied_by
                )
            else:
                s += u' (applied at %s)' % self.applied_at
        return s

class ChangeAttributeRequest(ChangeRequest):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    attribute = models.CharField(max_length=100)
    value = models.TextField(blank = True)
    
    def apply(self, user=None):
        obj = self.content_object
        setattr(obj, self.attribute, self.value)
        obj.save()
        super(ChangeAttributeRequest, self).apply(user)
    
    def request_description(self):
        return u'Change "%s" to "%s" on <%s>' % (
            self.attribute, self.value, self.content_object
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
        super(CreateObjectRequest, self).apply(user)
    
    def request_description(self):
        return u'Create a %s with attributes %s' % (
            self.content_type, self.attributes
        )

class DeleteObjectRequest(ChangeRequest):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    def apply(self, user=None):
        obj = self.content_object
        obj.delete()
        super(DeleteObjectRequest, self).apply(user)
    
    def request_description(self):
        return u'Delete %s' % self.content_object