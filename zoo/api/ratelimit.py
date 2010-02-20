from redis_db import r
from django.core.cache import cache # Because redis can't expire counters
from functools import update_wrapper
from utils import api_response

class RateFail(Exception):
    pass

class BadKeyError(RateFail):
    def code_and_description(self):
        return ('invalid-key', 'Invalid API key')

class RateExceededError(RateFail):
    def code_and_description(self):
        return ('rate-exceeded', 'Rate limit exceeded')

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
        key = key.encode('utf8')
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
    max_per_minute = 20
    max_per_5_second_burst = 3

class KeyRateLimiter(RateLimiter):
    def check(self, key):
        group_id = r.get('apikey:%s' % key)
        if not group_id:
            raise BadKeyError, 'Key does not exist'
        group_info = r.get('apikeygroup:%s' % group_id)
        if not group_info:
            raise BadKeyError, 'Key does not belong to a valid group'
        self.max_per_day, self.max_per_hour, self.max_per_minute, \
            self.max_per_5_second_burst = map(int, group_info.split(':'))
        return super(KeyRateLimiter, self).check(key)

def ratelimit(view_fn):
    def wrapper(request, *args, **kwargs):
        if 'api_key' in request.GET:
            limiter = KeyRateLimiter()
            key = request.GET['api_key']
        else:
            limiter = IPRateLimiter()
            key = request.META['REMOTE_ADDR']
        try:
            limiter.check(key)
        except RateFail, e:
            code, description = e.code_and_description()
            detail = e.message
            return api_response(request, 403, {
                'ok': False,
                'error': {
                    'code': code,
                    'description': description,
                    'detail': detail,
                },
                'key': key,
            })
        return view_fn(request, *args, **kwargs)
    
    update_wrapper(wrapper, view_fn)
    return wrapper