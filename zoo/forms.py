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
    delete = forms.BooleanField(required=False,
                                widget=SubmitInput(attrs={'value':"Delete"}))

class UndeleteForm(forms.Form):
    undelete = forms.BooleanField(required=False,
                                  widget=SubmitInput(attrs={'value':"Undo deletion"}))

class ExtraSubForm(forms.Form):
    add = forms.BooleanField(required=False,
                             widget=SubmitInput(attrs={'value':"Add"}))
    new_ids = forms.CharField(required=False,
                              widget=forms.HiddenInput)

    def __unicode__(self):
        return mark_safe(u''.join(unicode(bf) for bf in self))

class DeletedException(Exception):
    """This is thrown when a subform (for a new record, not an existing one)
    discovers that it has been deleted"""
    pass

class UberForm(object):
    def __init__(self, instance=None, data=None, prefix="", new_form_counter=None):
        if prefix:
            prefix += '-'

        self.instance = instance
        self.deleted = False
        if instance:
            prefix += '%s' % instance.pk
        else:
            prefix += 'new%s' % new_form_counter

        self.delete_form = DeleteForm(data=data,
                                      prefix=prefix)

        self.undelete_form = UndeleteForm(data=data,
                                          prefix=prefix)

        if data:
            assert self.delete_form.is_valid()
            self.deleted = self.delete_form.cleaned_data['delete']

            if self.deleted:
                if instance:
                    pass
                else:
                    # bail out!
                    raise DeletedException

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

                new_ids = ''
                if data:
                    esf = ExtraSubForm(data=data, prefix=sub_prefix)
                    # do this now so we can see the count,
                    # and increment it if necessary
                    assert esf.is_valid(), (esf.errors, data)
                    new_ids = esf.cleaned_data['new_ids'].split(',')
                    print new_ids
                    new_ids = map(int, new_ids)
                    new_ids.sort()
                    
                    if esf.cleaned_data['add']:
                        try:
                            max_id = max(new_ids)
                        except ValueError:
                            max_id = 1
                        new_ids.append(max_id + 1)

                for obj in objects:
                    suf = sub_uber_form_klass(obj, data, sub_prefix)
                    subuforms.append(suf)

                deleted_ids = set()
                for form_id in new_ids:
                    try:
                        suf = sub_uber_form_klass(None, data, sub_prefix, form_id)
                        subuforms.append(suf)
                    except DeletedException:
                        deleted_ids.add(form_counter)

                new_ids = sorted(set(new_ids) - deleted_ids)

                esf = ExtraSubForm(initial={'new_ids': ','.join(str(x) for x in new_ids),
                                            'add': ''},
                                   prefix=sub_prefix)


                form_sd[name] = {
                    'subuforms': subuforms,
                    'addform': esf,
                    }

        self.boundforms = form_sd

    def render_deleted(self):
        forms = []

        self.forall_forms(lambda f: forms.append(f))
        out = []
        for form in forms:
            for f in form:
                out.append(f.as_hidden())

        from pprint import pprint
        pprint(out)

        return mark_safe('\n'.join(out))

    def forall_forms(self, func):
        for name, f in self.boundforms.iteritems():
            if isinstance(f, dict):
                suf = f.get('subuforms')
                if suf:
                    for uf in suf:
                        uf.forall_forms(func)
                func(f['addform'])
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
                # new object
                pass
        
        self.forall_uf(get_changes)

        return changes


    def __getitem__(self, name):
        return self.boundforms[name]

    def __iter__(self):
        return self.boundforms.itervalues()

    parts = []



