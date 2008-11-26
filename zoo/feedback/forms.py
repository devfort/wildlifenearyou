from django import forms
from models import Feedback

class AnonymousForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('body', 'email')

class LoggedInForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('body')

def form_for_request(request):
    if request.user.is_anonymous():
        return AnonymousForm
    else:
        return LoggedInForm
