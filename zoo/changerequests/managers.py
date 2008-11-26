from django.db import models

class PendingChangeRequestManager(models.Manager):
    def get_query_set(self):
        return super(PendingChangeRequestManager, self).get_query_set().filter(applied_by__isnull=True)
