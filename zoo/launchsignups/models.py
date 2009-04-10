from django.db import models

class Signup(models.Model):
    email = models.EmailField()
    created = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return self.email


