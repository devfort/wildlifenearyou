from zoo.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpResponseRedirect as Redirect

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

def welcome(request):
    # Just to show people that they are logged in, really
    return render(request, 'accounts/welcome.html', {
        'user': request.user,
    })

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Ugly but necessary
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return Redirect('/')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {
        'form': form,
    })

@login_required
def profile_default(request):
    return Redirect(u'/profile/%s' % (request.user,))

def profile(request, username):
    user = get_object_or_404(User, username = username)
    return render(request, 'accounts/profile.html', {
        'profile_user': user
    })

def profile_edit(request, username):
    pass

from django import forms

class RegistrationForm(forms.ModelForm):
    username = forms.RegexField(
        label = _("Username"), max_length = 30, regex = r'^\w+$',
        help_text = _(
            "Required. 30 characters or fewer. Alphanumeric characters " +
            "only (letters, digits and underscores)."
        ),
        error_message = _(
            "This value must contain only letters, numbers and underscores."
        )
    )
    password1 = forms.CharField(
        label = _("Password"),
        widget = forms.PasswordInput
    )
    password2 = forms.CharField(
        label= _ ("Password confirmation"),
        widget=forms.PasswordInput
    )
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_(
            "A user with that username already exists."
        ))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_(
                "The two password fields didn't match."
            ))
        return password2

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
