from django.db import models
from django import forms
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
from django.forms.util import flatatt

class SubmitInput(forms.Widget):
    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, type='submit', name=name)
        return mark_safe(u'<input%s />' % flatatt(final_attrs))

    def value_from_datadict(self, data, files, name):
        if name not in data:
            # A missing value means False because HTML form submission does not
            # send results for non-clicked submit buttons.
            return False
        return super(SubmitInput, self).value_from_datadict(data, files, name)

class DeleteForm(forms.Form):
    delete = forms.BooleanField(required=False)

class ExtraSubForm(forms.Form):
    add = forms.BooleanField(required=False,
                             widget=SubmitInput(attrs={'value':"Add"}))
    count = forms.IntegerField(required=True,
                               widget=forms.HiddenInput)

    def __unicode__(self):
        return mark_safe(u''.join(unicode(bf) for bf in self))


class UberForm(object):
    def __init__(self, instance=None, data=None, prefix="", new_form_counter=None):
        if prefix:
            prefix += '-'

        self.instance = instance
        if instance:
            prefix += '%s' % instance.pk
        else:
            prefix += 'new%s' % new_form_counter

        self.delete_form = DeleteForm(data=data,
                                      prefix=prefix)

        form_sd = SortedDict()

        for part in self.parts:
            if len(part) == 2:
                name, form_klass = part
                form_sd[name] = form_klass(instance=instance,
                                           data=data,
                                           prefix=prefix)
            else:
                name, sub_uber_form_klass, object_getter = part
                objects = list(object_getter(instance))
                subuforms = []
                sub_prefix = "%s__%s" % (prefix, name)

                extra_count = 0
                if data:
                    esf = ExtraSubForm(data=data, prefix=sub_prefix)
                    # do this now so we can see the count,
                    # and increment it if necessary
                    assert esf.is_valid(), esf.errors
                    extra_count = esf.cleaned_data['count']
                    if esf.cleaned_data['add']:
                        extra_count += 1

                esf = ExtraSubForm(initial={'count': extra_count,
                                            'add': ''},
                                   prefix=sub_prefix)

                for obj in objects:
                    suf = sub_uber_form_klass(obj, data, sub_prefix)
                    subuforms.append(suf)

                for form_counter in range(1, extra_count + 1):
                    suf = sub_uber_form_klass(None, data, sub_prefix, form_counter)
                    subuforms.append(suf)

                form_sd[name] = {
                    'subuforms': subuforms,
                    'addform': esf,
                    }

        self.boundforms = form_sd

    def forall_forms(self, func):
        for name, f in self.boundforms.iteritems():
            if isinstance(f, dict):
                suf = f.get('subuforms')
                if suf:
                    for uf in suf:
                        uf.forall_forms(func)
            else:
                func(f)

    def forall_uf(self, func):
        func(self)
        
        for name, f in self.boundforms.iteritems():
            if isinstance(f, dict):
                suf = f.get('subuforms')
                if suf:
                    for uf in suf:
                        uf.forall_uf(func)

    def is_valid(self):
        is_valid = [True]

        def iv(form):
            if not form.is_valid():
                is_valid[0] = False

        self.forall_forms(iv)

        return is_valid[0]

    def immediate_forms(self):
        return [f for f in self
                if not isinstance(f, dict)]

    def changes(self):
        changes = SortedDict()

        def get_changes(uf):
            if uf.instance:
                # existing
                instance_dict = forms.models.model_to_dict(uf.instance)
                for f in uf.immediate_forms():
                    for name, val in f.cleaned_data.iteritems():
                        oldval = instance_dict[name]
                        
                        if val != oldval:
                            changes[(uf.instance, name)] = \
                                (oldval, val)
            else:
                pass
                # new object
        
        self.forall_uf(get_changes)

        return changes


    def __getitem__(self, name):
        return self.boundforms[name]

    def __iter__(self):
        return self.boundforms.itervalues()

    parts = []



