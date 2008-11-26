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

        if instance:
            prefix += '%s' % instance.pk
        else:
            prefix += 'new%s' % new_form_counter

        form_sd = SortedDict()
        form_sd['delete_form'] = DeleteForm(data=data,
                                            prefix=prefix)

        for part in self.parts:
            if len(part) == 2:
                name, form_klass = part
                form_sd[name] = form_klass(instance=instance,
                                           data=data,
                                           prefix=prefix)
            else:
                name, sub_uber_form_klass, object_getter = part
                objects = object_getter(instance)
                subforms = []
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
                    subforms.append(suf.boundforms)

                for form_counter in range(1, extra_count + 1):
                    suf = sub_uber_form_klass(None, data, sub_prefix, form_counter)
                    subforms.append(suf.boundforms)

                form_sd[name] = {
                    'subforms': subforms,
                    'addform': esf,
                    }

        self.boundforms = form_sd

    def is_valid(self, name):
        is_valid = True
        for name, f in self.boundforms.iteritems():
            try:
                for uf in f['subforms']:
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

    parts = []



