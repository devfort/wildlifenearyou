from django.db import models

class Feedback(models.Model):
    user = models.ForeignKey('auth.User', blank = True, null = True, 
        related_name='feedback_sumbissions'
    )
    email = models.EmailField(blank = True, help_text = 'Enter your e-mail if you want a reply')
    ip_address = models.CharField(max_length = 40, blank = True)
    from_page = models.CharField(max_length = 255, blank = True)
    created = models.DateTimeField(auto_now_add = True)
    body = models.TextField()
    
    def __unicode__(self):
        if self.user:
            return u'Feedback from %s on %s' % (
                self.user, self.created.date()
            )
        elif self.email:
            return u'Feedback from %s on %s' % (
                self.email, self.created.date()
            )
        else:
            return u'Anonymous feedback on %s' % self.created.date()
