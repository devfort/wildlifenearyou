from zoo.accounts.models import Profile
from django_openid.registration import RegistrationConsumer
from django_openid.forms import RegistrationForm
from django.http import HttpResponseRedirect
from django.conf import settings

class CustomRegistrationForm(RegistrationForm):
    extra_required = ('email',) # first/last name are optional
    
    def __init__(self, *args, **kwargs):
        kwargs['reserved_usernames'] = settings.RESERVED_USERNAMES
        super(CustomRegistrationForm, self).__init__(*args, **kwargs)
        
    class Meta(RegistrationForm.Meta):
        fields = ('username', 'email')

class RegistrationConsumer(RegistrationConsumer):
    base_template = 'base.html'
    on_complete_url = '/account/complete/'
    trust_root = '/account/'
    
    RegistrationForm = CustomRegistrationForm
    
    def user_can_login(self, request, user):
        # User must have validated their e-mail address
        
        return True
        
        return user.is_active and user.get_profile().email_validated
    
    def show_you_cannot_login(self, request, user, openid):
        message = 'You cannot log in with that account'
        if not user.is_active:
            message = 'Your account has been disabled.'
        if not user.get_profile().email_validated:
            message = 'You have not yet validated your e-mail address.'
        return self.show_message(
            request, 'You cannot log in', message,
        )
    
    def create_user(self, request, data, openid=None):
        user = super(RegistrationConsumer, self).create_user(
            request, data, openid
        )
        # Create their Profile
        Profile.objects.create(user=user)
        return user
    
    def on_registration_complete(self, request):
        return HttpResponseRedirect('/%s/' % request.user.username)

endpoint = RegistrationConsumer()