from django.http import HttpResponseRedirect
from django.db.models.signals import pre_save
import datetime, threading

class OnlyLowercaseUrls:
    def process_request(self, request):
        if request.path.lower() != request.path:
            return HttpResponseRedirect(request.path.lower())

stash = threading.local()
stash.current_user = None

def onanymodel_presave(sender, **kwargs):
    current_user = stash.current_user
    if not current_user.is_authenticated():
        current_user = None
    
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
        stash.current_user = request.user
