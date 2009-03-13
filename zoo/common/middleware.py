"""
Various custom middlewares used by the site. We also use this file as a way 
of getting some initialisation code to run only once (the initialise() method
that starts up our searchify search integration logic). This is not ideal, 
since middleware is only executed by a first incoming web request and hence 
is not triggered for command line tools or the ./manage.py shell. It will have
to do for the moment though.
"""
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from django.template.loader import render_to_string
import datetime, threading

from django.contrib.auth.models import User
from accounts.models import profilecalc_postsave

##### Save current user in a thread local and auto-populate created_by etc

stash = threading.local()
def set_current_user(user):
    stash.current_user = user

set_current_user(None)

def onanymodel_presave(sender, **kwargs):
    current_user = stash.current_user
    if current_user is None or not current_user.is_authenticated():
        # this will throw an exception if there's no sedf user AND THIS IS A
        # GOOD THING
        current_user = User.objects.get(username='sedf')

    obj = kwargs['instance']
    if hasattr(obj, 'modified_at'):
        obj.modified_at = datetime.datetime.now()
    if hasattr(obj, 'modified_by_id'):
        obj.modified_by = current_user
    if not obj.pk:
        if hasattr(obj, 'created_at'):
            obj.created_at = datetime.datetime.now()
        if hasattr(obj, 'created_by_id'):
            obj.created_by = current_user

pre_save.connect(onanymodel_presave)

class AutoCreatedAndModifiedFields:
    def process_request(self, request):
        set_current_user(request.user)

##### Profiles have a percentage completion which needs recalculating when certain related models change
post_save.connect(profilecalc_postsave)

##### Hook up searchify/djape magic
if settings.SEARCH_ENABLED:
    from searchify import initialise
    initialise()

class Custom403(object):
    """Catches a 403 response and renders a 403.html template"""

    def process_response(self, request, response):
        if isinstance(response, HttpResponseForbidden):
            return HttpResponseForbidden(render_to_string('403.html', { 'content': response.content }))
        else:
            return response
