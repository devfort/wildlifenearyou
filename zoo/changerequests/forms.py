from django import forms

from zoo.changerequests.models import ChangeRequest

class ChangeRequestActionForm(forms.Form):
    action = forms.ChoiceField(choices=[(x, x) for x in ('apply', 'delete', 'force')])
    changerequest = forms.ModelChoiceField(ChangeRequest.objects.filter(applied_by__isnull=True))

    def clean(self):
        action = self.cleaned_data.get('action', None)
        cr = self.cleaned_data.get('changerequest', None)

        if action == 'apply' and cr and cr.get_real().conflicts():
            raise forms.ValidationError("Race condition.")

        return self.cleaned_data

    def clean_changerequest(self):
        cr = self.cleaned_data['changerequest']
        if cr.subclass == 'CreateObjectRequest' and \
                    cr.createobjectrequest.parent is not None:
            raise forms.ValidationError(
                "Refusing to apply a child of a nested creation request"
            )
        return cr
