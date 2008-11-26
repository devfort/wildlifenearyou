import datetime, md5
from django.conf import settings

def attrproperty(getter_function):
    ''' usage:
    >>> class Foo(object):
    >>>     @attrproperty
    >>>     def subobject(self, name):
    >>>         if name == 'hello':
    >>>             return 1
    >>>         else:
    >>>             return 2

    >>> foo = Foo
    >>> foo.subobject.a
    2
    >>> foo.subobject.b
    2
    >>> foo.subobject.hello
    1

    '''
    class _Object(object):
        def __init__(self, obj):
            self.obj = obj
        def __getattr__(self, attr):
            return getter_function(self.obj, attr)

    return property(_Object)

def send_mail(subject, message, from_email, recipient_list, fail_silently=False, auth_user=None, auth_password=None):
    from django.core.mail import send_mail
    if settings.DEBUG:
        print """Sending email to %s from %s

subject: %s
body:
%s
""" % (recipient_list, from_email, subject, message)
    else:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False, auth_user=None, auth_password=None)

