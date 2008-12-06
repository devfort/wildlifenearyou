from django import forms
from django.db import models
from django.utils import simplejson

class JSONField(models.Field):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return 'TextField'

    def to_python(self, value):
        if value is None or value in ('', u''):
            return value

        if isinstance(value, basestring):
            attr = simplejson.loads(value)
            return dict([(str(k), v) for k, v in attr.iteritems()])

        return value

    def get_db_prep_save(self, value):
        if not isinstance(value, basestring):
            return simplejson.dumps(value)
        return value

    def get_db_prep_lookup(self, lookup_type, value):
        raise NotImplementedError(
            "Don't try to look up data by a JSON field. It's just stupid."
        )
