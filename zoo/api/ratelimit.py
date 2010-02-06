from redis_db import r
from django.core.cache import cache # Because redis can't expire counters

class RateFail(Exception):
    pass

class BadKeyError(RateFail):
    pass

class RateExceededError(RateFail):
    pass

class RateLimiter(object):
    max_per_day = 0
    max_per_hour = 0
    max_per_minute = 0
    max_per_5_second_burst = 0
    
    def incr_check(self, key, max, timeout):
        cache._cache.add(key, 0, timeout)
        i = cache.incr(key)
        if i <= max:
            return True
        else:
            return False
    
    def check(self, key):
        exc = None
        if not self.incr_check(
            'ratelimit-day:%s' % key, self.max_per_day, 60 * 60 * 24
        ):
            exc = RateExceededError('Max %s per day' % self.max_per_day)
        if not self.incr_check(
            'ratelimit-hour:%s' % key, self.max_per_hour, 60 * 60
        ):
            exc = RateExceededError('Max %s per hour' % self.max_per_hour)
        if not self.incr_check(
            'ratelimit-minute:%s' % key, self.max_per_minute, 60
        ):
            exc = RateExceededError('Max %s per minute' % self.max_per_minute)
        if not self.incr_check(
            'ratelimit-5-second:%s' % key, self.max_per_5_second_burst, 5
        ):
            exc = RateExceededError('Max burst %s in 5 seconds' % (
                self.max_per_5_second_burst
            ))
        if exc is not None:
            raise exc
        else:
            return True

class IPRateLimiter(RateLimiter):
    max_per_day = 1000
    max_per_hour = 1000
    max_per_minute = 60
    max_per_5_second_burst = 5

class KeyRateLimiter(RateLimiter):
    def check(self, key):
        group_id = r.get('apikey:%s' % key)
        if not group_id:
            raise BadKeyError, 'Key does not exist'
        group_info = r.get('apikeygroup:%s' % group_id)
        if not group_info:
            raise BadKeyError, 'Key group is not defined'
        self.max_per_day, self.max_per_hour, self.max_per_minute, \
            self.max_per_5_second_burst = map(int, group_info.split(':'))
        return super(KeyRateLimiter, self).check(key)

def ratelimit(fn):
    # This will be the magic decorator... just need to write the code
    pass
