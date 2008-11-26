from django import forms
from django.utils.datastructures import SortedDict

UF_DEFS = {}

class UberFormMetaClass(type):
    def __new__(cls, name, bases, attrs):
        klass = type.__new__(cls, name, bases, attrs)
        if klass.model: # not true for base
            UF_DEFS[klass.model] = klass
        return klass

class DeleteForm(forms.Form):
    delete = forms.BooleanField(required=False)


class UberForm(object):
    __metaclass__ = UberFormMetaClass
    
    def __init__(self, instance, data=None, prefix=""):
        if prefix != "":
            prefix += "__"
        prefix += '%s-%s' % (type(instance).__name__, instance.pk)

        kwargs = {
            'prefix': prefix,
        }

        if data:
            kwargs['data'] = data

        form_sd = SortedDict()
        form_sd['delete_form'] = DeleteForm(**kwargs)

        modelform_kwargs = kwargs.copy()
        modelform_kwargs['instance'] = instance

        for name, part in self.parts:
            if isinstance(part, type) and issubclass(part, forms.BaseForm):
                form_sd[name] = part(**kwargs)
            else:
                objects = part(instance)
                subforms = []
                for obj in objects:
                    sub_uber_form_klass = UF_DEFS[type(obj)]

                    suf = sub_uber_form_klass(obj, data, prefix)
                    subforms.append(suf.boundforms)
                form_sd[name] = subforms

        self.boundforms = form_sd

    def is_valid(self, name):
        is_valid = True
        for name, f in self.boundforms.iteritems():
            try:
                for uf in f:
                    if not uf.is_valid():
                        is_valid = False
            except TypeError:
                if not f.is_valid():
                    is_valid = False
        return is_valid

    def __getitem__(self, name):
        return self.boundforms[name]

    def __iter__(self):
        return self.boundforms.itervalues()

    model = None
    parts = []



