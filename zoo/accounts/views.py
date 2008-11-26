from zoo.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponseRedirect as Redirect
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect as Redirect

from zoo.accounts.models import Profile
from zoo.accounts.forms import RegistrationForm, OurAuthenticationForm, ProfileEditForm, UserEditProfileBitsForm

def welcome(request):
    # Just to show people that they are logged in, really
    return render(request, 'accounts/welcome.html', {
        'user': request.user,
    })

def login(request, template_name='registration/login.html', redirect_field_name=REDIRECT_FIELD_NAME):
    if request.user.is_authenticated():
        return Redirect('/')

    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = OurAuthenticationForm(data=request.POST)
        if form.is_valid():
            from django.contrib.auth import login
            login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
            return Redirect(redirect_to)
    else:
        form = OurAuthenticationForm(request)

    request.session.set_test_cookie()

    return render(request, template_name, {
        'form': form,
        redirect_field_name: redirect_to,
    })
login = never_cache(login)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            p = user.get_profile()
            p.send_validation_email()
            return Redirect(reverse('accounts-registration-complete'))
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {
        'form': form,
    })

def registration_complete(request):
    return render(request, 'accounts/registration_complete.html', {})

def validate_email(request, username, days, hash):
    user = get_object_or_404(User, username=username)
    p = user.get_profile()
    if p.hash_is_valid(days, hash):
        p.email_validated = True
        p.save()
        user.backend='django.contrib.auth.backends.ModelBackend'
        from django.contrib.auth import login
        login(request, user)
        # TODO: send welcome email
        return Redirect(reverse('validate-email-success'))
    return Redirect('/')

def validate_email_success(request):
    if not request.user.is_authenticated():
        if not request.user.get_profile.email_validated:
            raise Http404

    return render(request, 'accounts/email_validated.html', {})

@login_required
def profile_default(request):
    return Redirect(u'/profile/%s' % (request.user,))

def profile(request, username):
    user = get_object_or_404(User, username = username)
    return render(request, 'accounts/profile.html', {
        'profile': user.get_profile(),
    })

def profile_edit(request, username):
    user = get_object_or_404(User, username = username)
    profile = user.get_profile()
    if request.method == 'POST':
        f = ProfileEditForm(request.POST, instance=profile)
        f2 = UserEditProfileBitsForm(request.POST, instance=user)
        if f.is_valid() and f2.is_valid():
            f.save()
            f2.save()
            return Redirect(profile.get_absolute_url())
    else:
        f = ProfileEditForm(instance=profile)
        f2 = UserEditProfileBitsForm(instance=user)

    return render(request, 'accounts/profile_edit.html', {
        'profile': profile,
        'profile_form': f,
        'user_form': f2,
    })

def all_profiles(request):
    return render(request, 'accounts/all_profiles.html', {
        'all_users': User.objects.all(),
    })
