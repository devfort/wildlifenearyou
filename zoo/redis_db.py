from django.core import signals
from django.conf import settings
import redis

r = redis.Redis(
    host = getattr(settings, 'REDIS_HOST', 'localhost'),
    port = getattr(settings, 'REDIS_PORT', 6379),
    db = getattr(settings, 'REDIS_DB', 1),
)

# Disconnect at end of every request (auto-connects on next command)
def on_finish_disconnect(**kwargs):
    r.disconnect()
signals.request_finished.connect(on_finish_disconnect)
