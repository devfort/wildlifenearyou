from django_openid.registration import RegistrationConsumer, RegistrationForm

class SinglePasswordRegistrationForm(RegistrationForm):
    extra_required = ('email',) # first/last name are optional
    
    def __init__(self, *args, **kwargs):
        kwargs['reserved_usernames'] = settings.RESERVED_USERNAMES
        super(RF, self).__init__(*args, **kwargs)
        # We only ask for their password once
        del self.fields['password2']
        
    class Meta(RegistrationForm.Meta):
        fields = ('username', 'email')

class RegistrationConsumer(RegistrationConsumer):
    
    def user_can_login(self, request, user):
        # User must have validated their e-mail address
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
    
    def save_form(self, form):
        # Create their Profile
        user = super(RegistrationConsumer, self).save_form(form)
        Profile.objects.create(user=user)
        return user
    
    def get_registration_form_class(self, request):
        return SinglePasswordRegistrationForm
