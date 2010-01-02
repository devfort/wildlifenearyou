from django.db import models

class Event(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    type = models.CharField(max_length = 50)
    description = models.TextField()
    user = models.ForeignKey('auth.User', blank = True, null = True)
    custom_1 = models.CharField(max_length = 255, blank = True)
    custom_2 = models.CharField(max_length = 255, blank = True)
    custom_3 = models.CharField(max_length = 255, blank = True)
    url = models.CharField(max_length = 255, blank = True)
    
    def __unicode__(self):
        return self.description
