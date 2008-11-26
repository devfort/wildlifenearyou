from django import forms

from zoo.changerequests.models import ChangeRequest

class ChangeRequestActionForm(forms.Form):
    action = forms.ChoiceField(choices=[(x, x) for x in ('apply', 'delete', 'force')])
    changerequest = forms.ModelChoiceField(ChangeRequest.objects.all())
