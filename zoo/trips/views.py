from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect as Redirect
from django.contrib.auth.decorators import login_required

from zoo.shortcuts import render
from zoo.trips.models import Trip
from zoo.accounts.models import Profile
from zoo.animals.forms import SpeciesField

@login_required
def logbook_default(request):
    return Redirect(reverse('logbook', args=(request.user,)))

def logbook(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'trips/logbook.html', {
        'logbook': user.created_trip_set.all(),
        'profile': user.get_profile(),
    })

def trip_edit(request, username):
    pass

@login_required
def trip_add(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = AddTripForm(request.POST)
        if form.is_valid():
            trip = form.save()
            return Redirect(reverse('trip-view', args=(trip.id,)))
    else:
        form = AddTripForm()
    
    return render(request, 'trips/add_trip.html', {
        'profile': user.get_profile(),
        'form': form,
    })
    
def trip_view(request, username, trip_id):
    user = get_object_or_404(User, username=username)
    trip = get_object_or_404(Trip, id=trip_id)
    return render(request, 'trips/trip.html', {
        'profile': user.get_profile(),
        'trip': trip,
    })

    
from django import forms

class AddTripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ('name', 'description', 'start', 'end')

    def save(self):
        trip = super(AddTripForm, self).save(commit=False)
        trip.save()
        Trips.objects.create(trip=trip)
        return trip

from zoo.places.models import Place, Country
from zoo.animals.models import Species

def add_sightings(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)
    assert False, request.POST