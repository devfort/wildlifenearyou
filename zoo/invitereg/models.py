from django.db import models

class InviteCode(models.Model):
    code = models.CharField(max_length = 20)
    claimed = models.BooleanField(default = False)
    claimed_at = models.DateTimeField(null = True, blank = True)
    claimed_by = models.ForeignKey('auth.User', blank = True, null = True)
    
    def __unicode__(self):
        return u'%s (claimed: %s)' % (self.code, self.claimed)
