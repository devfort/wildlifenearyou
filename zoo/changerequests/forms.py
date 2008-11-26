from django import forms

from zoo.changerequests.models import ChangeRequest

class ChangeRequestActionForm(forms.Form):
    action = forms.ChoiceField(choices=[(x, x) for x in ('apply', 'delete', 'force')])
    changerequest = forms.ModelChoiceField(ChangeRequest.objects.all())

    def clean(self):
        action = self.cleaned_data.get('action', None)
        cr = self.cleaned_data.get('changerequest', None)

        if action == 'apply' and cr and cr.get_real().conflicts():
            raise forms.ValidationError("Race condition.")

        return self.cleaned_data
