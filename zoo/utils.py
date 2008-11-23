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
