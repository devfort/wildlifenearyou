from django.db import models
from django.contrib.auth.models import User

class AuditedModel(models.Model):
    created_at = models.DateTimeField(null=False, blank=False)
    created_by = models.ForeignKey(User, related_name='created_%(class)s_set', null=False, blank=False)
    modified_at = models.DateTimeField(null=False, blank=False)
    modified_by = models.ForeignKey(User, related_name='modified_%(class)s_set', null=False, blank=False)

    class Meta:
        abstract = True
