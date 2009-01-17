from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.conf import settings

from zoo.accounts.models import Profile

class RegistrationForm(forms.ModelForm):
    username = forms.RegexField(
        label = _("Username"), max_length = 30, regex = r'^\w{3,}$',
        help_text = _(
            "Required, 3-30 characters. Alphanumeric characters " +
            "only (letters, digits and underscores)."
        ),
        error_message = _(
            "This value must contain only letters, numbers and underscores."
        )
    )
    password = forms.CharField(
        label = _("Password"),
        widget = forms.PasswordInput,
    )
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_username(self):
        username = self.cleaned_data["username"]
        if username in settings.RESERVED_USERNAMES:
            raise forms.ValidationError(_(
                "That username is not available."
            ))
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_(
            "A user with that username already exists."
        ))

    def save(self):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.save()
        Profile.objects.create(user=user)
        return user

class OurAuthenticationForm(AuthenticationForm):
    """
    We need to check for email validation as well so we need to
    override the entire clean method to add two lines which is
    unfortunate.

    We could check after form validation and then redirect to another page
    or add the errors manually to the form but this would involve
    creating an ErrorList. Any method seems to have to involve
    duplicating Django auth code. Subclassing the AuthenticationForm
    and checking email validation there seems to be the best option.
    """

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_(
                    "Please enter a correct username and password. Note that your password is case-sensitive."
                ))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_("This account is inactive."))
            if not self.user_cache.get_profile().email_validated:
                raise forms.ValidationError(_(
                    "You must validate your email address before logging in. Check your email!"
                ))

        # TODO: determine whether this should move to its own method.
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError(_("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in."))

        return self.cleaned_data

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['biography', 'url']

class UserEditProfileBitsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
