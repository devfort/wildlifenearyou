from django.db import models
from shorturl.utils import converter
import random
from redis_db import r

class ApiKeyGroup(models.Model):
    name = models.CharField(max_length = 100, default='default')
    max_per_day = models.IntegerField(default = 60 * 30 * 24)
    max_per_hour = models.IntegerField(default = 60 * 30)
    max_per_minute = models.IntegerField(default = 30)
    max_per_5_second_burst = models.IntegerField(default = 10)
    
    def save(self, *args, **kwargs):
        super(ApiKeyGroup, self).save(*args, **kwargs)
        r.set('apikeygroup:%s' % self.pk, '%s:%s:%s:%s' % (
            self.max_per_day, self.max_per_hour, self.max_per_minute,
            self.max_per_5_second_burst
        ))
    
    def __unicode__(self):
        return self.name

class ApiKey(models.Model):
    user = models.ForeignKey('auth.User', related_name = 'api_keys')
    group = models.ForeignKey(ApiKeyGroup)
    key = models.CharField(max_length = 20, unique = True, db_index = True)
    purpose = models.TextField(blank = True)
    created_at = models.DateTimeField(auto_now_add = True)
    num_calls = models.IntegerField(default = 0)
    
    def __unicode__(self):
        return u'%s for user %s' % (self.key, self.user)
    
    def save(self, *args, **kwargs):
        super(ApiKey, self).save(*args, **kwargs)
        r.set('apikey:%s' % self.key, self.group.pk)
    
    def delete(self, *args, **kwargs):
        super(ApiKey, self).delete(*args, **kwargs)
        r.delete('apikey:%s' % self.key)
    
    @classmethod
    def create_for_user(cls, user, group, purpose = ''):
        def rand_key():
            return ''.join([
                random.choice(converter.digits) for r in range(12)
            ])
        key = rand_key()
        while cls.objects.filter(key = key).count():
            key = rand_key()
        return cls.objects.create(
            user = user,
            group = group,
            key = key,
            purpose = purpose,
        )
