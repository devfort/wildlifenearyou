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
from django import forms

from zoo.accounts.models import Profile
from zoo.animals.models import Species
from zoo.accounts.forms import RegistrationForm, OurAuthenticationForm, ProfileEditForm, UserEditProfileBitsForm
from zoo.search import nearest_places_with_species

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
    if request.user.is_authenticated():
        return Redirect('/')

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
        p.send_welcome_email()
        return Redirect(reverse('validate-email-success'))
    return Redirect('/')

def validate_email_success(request):
    if not request.user.is_authenticated():
        if not request.user.get_profile.email_validated:
            raise Http404

    return render(request, 'accounts/email_validated.html', {})

class ForgottenPassword(forms.Form):
    username_or_email = forms.CharField(max_length=75)

    def clean_username_or_email(self):
        submitted = self.cleaned_data['username_or_email']
        try:
            if '@' in submitted:
                what_submitted = "email address"
                user = User.objects.get(email=submitted)
            else:
                what_submitted = "username"
                user = User.objects.get(username=submitted)
        except User.DoesNotExist:
            raise forms.ValidationError("The %s you submitted wasn't found. Please check it and try again!" % what_submitted)
        return user

def forgotten_password(request):
    if request.user.is_authenticated():
        return Redirect('/')

    if request.method == 'POST':
        form = ForgottenPassword(data=request.POST)
        if form.is_valid():
            user = form.cleaned_data['username_or_email']
            user.get_profile().send_password_key_email()
            return Redirect(reverse('password-key-sent'))
    else:
        form = ForgottenPassword()

    return render(request, 'accounts/forgotten_password.html', {
        'form': form,
    })

def recover_password(request, username, days, hash):
    if request.user.is_authenticated():
        return Redirect('/')

    user = get_object_or_404(User, username=username)
    if user.get_profile().hash_is_valid(days, hash):
        user.backend='django.contrib.auth.backends.ModelBackend'
        from django.contrib.auth import login
        login(request, user)
        return Redirect(reverse('change-password'))
    else:
        return Redirect('/')

def password_key_sent(request):
    if request.user.is_authenticated():
        return Redirect('/')
    return render(request, 'accounts/password_key_sent.html', {})

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
            profile.recalculate_percentage_complete()
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

def delete_location(request):
    """Remove location"""
    if not request.user.is_anonymous():
        profile = request.user.get_profile()
        profile.location = ''
        profile.latitude = None
        profile.longitude = None
        profile.save()
    else:
        response = Redirect('/set-location/?done')
        response.set_cookie(
            key = 'location',
            value = '',
            path = '/',
        )
        return response
    msg = 'Your location has been removed.'
    return render(request, 'accounts/set_location.html', {
        'msg': msg,
        'current_location': '',
    })

from zoo.utils import location_from_request
def set_location(request):
    """
    Logged in users use this view to set the location on their profile -
    anonymous users get a cookie instead
    """
    from zoo.search import search_locations
    (current_location, (lat, lon)) = location_from_request(request)

    location = request.POST.get('location', '')
    msg = ''

    if location:
        results = list(search_locations(location))
        if len(results):
            result = results[0]
            (lat, lon) = result['latlon']
            description = result['description']
            msg = 'Your location has been set to <strong>%s</strong>.' % description
            try:
                random_animal = Species.objects.order_by('?')[0]
                nearest = nearest_places_with_species(random_animal.common_name, (lat, lon))
                msg += ' As an example, your nearest <a href="%s">%s</a> is %s miles away, at <a href="%s">%s</a>.' % (random_animal.urls.absolute, random_animal.common_name, int(nearest[0].distance_miles+0.5), nearest[0].urls.absolute, nearest[0])
            except IndexError:
                nearest = None
            current_location = description
            # Set their location
            if not request.user.is_anonymous():
                profile = request.user.get_profile()
                profile.location = description
                profile.latitude = lat
                profile.longitude = lon
                profile.save()
            else:
                # Set it in a cookie instead
                response = Redirect('/set-location/?done')
                response.set_cookie(
                    key = 'location',
                    value = '%s:%f,%f' % tuple(
                        [description] + result['latlon']
                    ),
                    path = '/',
                )
                return response
        else:
            msg = 'No matches for your search'
    return render(request, 'accounts/set_location.html', {
        'msg': msg,
        'current_location': current_location,
    })
