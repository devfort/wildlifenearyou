from django.http import HttpResponseRedirect
from django.db.models.signals import pre_save
import datetime, threading

from django.contrib.auth.models import User

class OnlyLowercaseUrls:
    def process_request(self, request):
        if request.path.lower() != request.path:
            return HttpResponseRedirect(request.path.lower())

stash = threading.local()
def set_current_user(user):
    stash.current_user = user

set_current_user(None)

def onanymodel_presave(sender, **kwargs):
    current_user = stash.current_user
    if current_user==None or not current_user.is_authenticated():
        # this will throw an exception if there's no sedf user AND THIS IS A GOOD THING
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
