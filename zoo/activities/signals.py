from django.db.models.signals import post_save, post_delete
from django.conf import settings
from django.contrib.auth.models import User
from models import Event

def on_save(sender, **kwargs):
    model_type = '%s.%s' % (sender._meta.app_label, sender._meta.object_name)
    if model_type not in settings.ACTIVITY_MODELS:
        return
    obj = kwargs['instance']
    if kwargs['created']:
        description = u"%s %s was created" % (sender._meta.object_name, obj)
        type = 'created'
    else:
        description = u"%s %s was updated" % (sender._meta.object_name, obj)
        type = 'updated'
    try:
        url = obj.get_absolute_url()
    except:
        url = ''
    
    # Is there a user?
    user = None
    for attr in ('modified_by', 'created_by', 'user'):
        potential = getattr(obj, attr, None)
        if potential and isinstance(potential, User):
            user = potential
            break
    
    Event.objects.create(
        type = type,
        description = description,
        user = user,
        url = url,
        custom_1 = model_type,
        custom_2 = obj.pk
    )

post_save.connect(on_save)

def on_delete(sender, **kwargs):
    model_type = '%s.%s' % (sender._meta.app_label, sender._meta.object_name)
    if model_type not in settings.ACTIVITY_MODELS:
        return
    obj = kwargs['instance']
    Event.objects.create(
        type = 'deleted',
        description = u'%s %s was deleted' % (sender._meta.object_name, obj),
        custom_1 = model_type,
        custom_2 = obj.pk
    )

post_delete.connect(on_delete)
