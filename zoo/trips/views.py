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
def tripbook_default(request):
    return Redirect(reverse('tripbook', args=(request.user,)))

def tripbook(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'trips/tripbook.html', {
        'tripbook': user.created_trip_set.all(),
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

import re
saw_key_re = re.compile('^saw_\d+$')
saw_id_key_re = re.compile('^saw_id_\d+$')
saw_selection_key_re = re.compile('^saw_selection_\d+$')


@login_required
def add_sightings(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)
    # request.POST will contain:
    #   saw_1, saw_2, ... = text strings the user said they saw
    #   saw_id_1, saw_id_2, ... = IDs of things we have resolved
    #   saw_selection_1, ... = IDs of things they have picked from our UI
    # 
    # Our aim is to change all of the saw_%s in to saw_id_%s
    # 
    # Every round-trip to the server that results in a saw_section will remove
    # an item from the saw_% list and add an item to the saw_id_% list
    # 
    # Just keep on looping around until they've got them all right, or 
    # they've given up on some of the ones that don't have any matches.
    # 
    # The IDs in saw_selection_% come in two forms - dj-% and x-%
    #   s-% means "this is a Species object ID (in our local db table)"
    #   x-% means "this is a Xapian ID" (in our Xapian index)
    # 
    # When we finally submit, any x-% ids will result in an insert in to our 
    # species table since they will represent animals that we don't officially
    # know anything about yet.
    
    # The collection of verified sighted species IDs
    saw_id_set = set(
        value for key, value in request.POST.items()
        if saw_id_key_re.match(key)
    )
    
    # Text items we haven't resolved yet
    saw_dict = dict([
        (int(key.replace('saw_', '')), value)
        for key, value in request.POST.items()
        if saw_key_re.match(key)
    ])
    
    # Selections for those (IDs should match IDs in the saw dict above)
    saw_selection_dict = dict([
        (int(key.replace('saw_selection_', '')), value)
        for key, value in request.POST.items()
        if saw_selection_key_re.match(key)
    ])
    
    # If we just have saw_ids, we can get right on with adding the sightings
    if saw_id_set and not saw_dict:
        return finish_add_sightings(request, place, saw_id_set)
    
    # If there's a saw_dict and they've picked an option for everything on it 
    # as represented in saw_selection_dict, we should sanity check each of 
    # their selections and then add the sightings
    #
    # We track which ones have been successfully looked up by removing them 
    # from saw_dict and adding them to the saw_id_set. If saw_dict is 
    # empty at the end then we've got them all!
    if saw_dict and saw_selection_dict:
        # They've picked some things
        
        # We'll iterate over IDs that are present in both dictionaries
        keys = [key for key in saw_dict if key in saw_selection_dict]
        
        for key in keys:
            string = saw_dict[key]
            selected_id = saw_selection_dict[key]
            
            # Look up selected_id
            if selected_id.startswith('x-'):
                x_id = selected_id.replace('x-', '')
                assert False, 'Look up Xapian document for %s here' % x_id
            elif selected_id.startswith('dj-'):
                dj_id = selected_id.replace('dj-', '')
                try:
                    species = Species.object.get(pk = dj_id)
                except Species.DoesNotExist:
                    found_them_all = False
                    continue
                saw_id_set.add(species.id)
                # And remove from saw_list
                del saw_dict[key]
            else:
                # Someone has been messing around with form vars - ignore
                continue
        if not saw_dict:
            return finish_add_sightings(request, place, saw_id_set)
    
    # If we get here, there are at least some "saw" text entries that need to 
    # be disambiguated. Show a form.
    from django import forms
    from zoo.search import search_species
    form = forms.Form()
    for key, string in saw_dict.items():
        if not string.strip():
            continue
        results = search_species(string)
        if not results:
            continue
        form.fields['saw_selection_%s' % key] = forms.ChoiceField(
            choices = [((
                    r.get('django_id') and 'dj-%s' % r['django_id'] 
                    or r['search_id']
                ), u'%s (%s)' % (r['common_name'], r['scientific_name']))
                for r in results
            ],
            widget = forms.RadioSelect
        )
    return render(request, 'trips/which-did-you-mean.html', {
        'form': form,
    })

def finish_add_sightings(request, place, saw_id_set):
    assert False, 'Add a sighting for %s to %s' % (saw_id_set, place)
