from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import \
    HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.contrib.auth.decorators import login_required
from django import forms
from django.template.defaultfilters import slugify

import datetime, urllib, re
from parsedatetime.parsedatetime import Calendar

from zoo.shortcuts import render
from zoo.trips.models import Trip, Sighting
from zoo.places.models import Place, Country
from zoo.animals.models import Species
from zoo.photos.models import Photo
from zoo.accounts.models import Profile
from zoo.animals.forms import SpeciesField
from zoo.search import NotFound, lookup_species, search_species
from zoo.trips.utils import lookup_xapian_or_django_id

import add_trip_utils

@login_required
def add_trip(request, country_code, slug):
    place = place = get_object_or_404(Place,
        slug = slug,
        country__country_code = country_code
    )
    
    selected = _get_selected(request.POST)
    unknowns = _get_unknowns(request.POST)
    
    if 'finish' in request.POST and (selected or unknowns):
        return finish_add_trip(request, place, selected, unknowns)
    
    q = request.REQUEST.get('q', '').strip()
    # Clear search if they selected one of the options
    if _add_selected_was_pressed(request.POST):
        q = ''
    
    results = []
    if q:
        # Search for 10 but only show the first 5, so our custom ordering 
        # that shows animals spotted here before can take effect
        results = add_trip_utils.search(q, limit=10, place=place)[:5]
    
    details = add_trip_utils.bulk_lookup(selected, place=place)
    
    return render(request, 'trips/add_trip.html', {
        'place': place,
        'results': results,
        'selected_details': details,
        'q': q,
        'unknowns': unknowns,
        'request_path': request.path,
        'debug': pformat(request.POST.lists())
    })

def ajax_search_species(request, country_code, slug):
    place = place = get_object_or_404(Place,
        slug = slug,
        country__country_code = country_code
    )
    q = request.GET.get('q', '')
    if len(q) >= 3:
        return render(request, 'trips/ajax_search_species.html', {
            'q': q,
            'results': add_trip_utils.search(q, limit=10, place=place)[:5],
        })
    else:
        return render(request, 'trips/_add_trip_help.html')

@login_required
def add_sightings_to_trip(request, username, trip_id):
    if username != request.user.username:
        return HttpResponse('You cannot edit this trip')
    trip = get_object_or_404(Trip,
        pk = trip_id, created_by__username = username
    )
    place = trip.place

    selected = _get_selected(request.POST)
    unknowns = _get_unknowns(request.POST)

    if 'finish' in request.POST and (selected or unknowns):
        return finish_add_sightings_to_trip(request, trip, selected, unknowns)

    q = request.REQUEST.get('q', '').strip()
    # Clear search if they selected one of the options
    if _add_selected_was_pressed(request.POST):
        q = ''

    results = []
    if q:
        # Search for 10 but only show the first 5, so our custom ordering 
        # that shows animals spotted here before can take effect
        results = add_trip_utils.search(q, limit=10, place=place)[:5]

    details = add_trip_utils.bulk_lookup(selected, place=place)

    return render(request, 'trips/add_trip.html', {
        'place': place,
        'trip': trip,
        'results': results,
        'selected_details': details,
        'q': q,
        'unknowns': unknowns,
        'request_path': request.path,
        'debug': pformat(request.POST.lists())
    })

@login_required
def finish_add_sightings_to_trip(request, trip, selected, unknowns):
    selected_details = add_trip_utils.bulk_lookup(selected)
    # Now save the selected and unknown sightings
    for i, details in enumerate(selected_details):
        trip.sightings.create(
            species = species_for_freebase_details(details),
            place = trip.place,
            note = ''
        )
    for i, name in enumerate(unknowns):
        trip.sightings.create(
            place = trip.place,
            species_inexact = name,
            note = ''
        )
    # And we're done!
    return HttpResponseRedirect(trip.get_absolute_url())

@login_required
def finish_add_trip(request, place, selected, unknowns):
    selected_details = add_trip_utils.bulk_lookup(selected)
    if 'add_trip_form_displayed' not in request.POST:
        # Display form for the first time
        form = AddTripForm(
            user = request.user,
            place = place,
            initial = {'name': 'My trip'}
        )
    else:
        form = AddTripForm(request.POST, user = request.user, place = place)
        if form.is_valid():
            trip = Trip(
                name = form.cleaned_data['name'],
                start = form.cleaned_data['start'],
                start_accuracy = form.cleaned_data['start_accuracy'],
                description = form.cleaned_data['description'],
                rating = form.cleaned_data['rating'],
                place = place,
            )
            trip.save()
            # Now save the selected and unknown sightings
            for i, details in enumerate(selected_details):
                trip.sightings.create(
                    species = species_for_freebase_details(details),
                    place = place,
                    note = request.POST.get('selected_note_%s' % i, ''),
                )
            for i, name in enumerate(unknowns):
                trip.sightings.create(
                    place = place,
                    species_inexact = name,
                    note = request.POST.get('unknown_note_%s' % i, ''),
                )
            # And we're done!
            return HttpResponseRedirect(trip.get_absolute_url())
    
    return render(request, 'trips/add_trip_final.html', {
        'form': form,
        'place': place,
        'selected': selected,
        'selected_details': selected_details,
        'unknowns': unknowns,
        'request_path': request.path,
    })

def species_for_freebase_details(details):
    "If species for that freebase ID exists, return it - otherwise create it"
    try:
        return Species.objects.get(freebase_id = details['id'])
    except Species.DoesNotExist:
        slug = slugify(details['name'].lower())
        while Species.objects.filter(slug = slug).count():
            slug = slug + '-'
        obj, created = Species.objects.get_or_create(
            freebase_id = details['id'],
            defaults = {
                'slug': slug,
                'common_name': details['name'],
                'latin_name': details.get('scientific_name') or '',
            }
        )
        return obj

from pprint import pformat

import re
selected_key_re = re.compile('^selected_(\d+)$')
add_selected_key_re = re.compile('^add_selected_(\d+)\.x$')
unknown_key_re = re.compile('^unknown_(\d+)$')

def _get_selected(POST):
    selected = []
    for key in POST.keys():
        selected_match = selected_key_re.match(key)
        if selected_match:
            i = selected_match.group(1)
            # Ensure it hasn't been deleted
            if ('remove_selected_%s.y' % i) not in POST:
                selected.append(POST[key])
            continue
        
        # Deal with keys that add things
        add_selected_match = add_selected_key_re.match(key)
        if add_selected_match:
            value_key = 'result_%s' % add_selected_match.group(1)
            if value_key in POST:
                selected.append(POST[value_key])
    
    return selected

def _get_unknowns(POST):
    unknowns = []
    for key in POST.keys():
        m = unknown_key_re.match(key)
        if m:
            i = m.group(1)
            # Has it been deleted?
            if ('remove_unknown_%s.y' % i) not in POST:
                unknowns.append(POST[key])
    
    if 'add_unknown' in POST or 'add_unknown.x' in POST:
        unknowns.append(POST['add_unknown_text'])
    
    return unknowns

def _add_selected_was_pressed(POST):
    return len([k for k in POST.keys() if add_selected_key_re.match(k)])

class AddTripForm(forms.ModelForm):
    # In the model this is a date, but we do some magic to allow more 
    # flexibility (see clean_start below).
    start = forms.CharField(required = False, label='Trip date')
    # And this has to be there or it won't be saved
    start_accuracy = forms.CharField(
        required = False, label='Start accuracy (hidden)'
    )
    # Override the default for this, since we need it to match the widget 
    # we're using
    rating = forms.ChoiceField(
        required = False, choices=[(i, i) for i in range(1, 6)]
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        place = kwargs.pop('place', None)
        super(AddTripForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Trip title'
        self.fields['description'].label = 'Your thoughts on this place'
        self.fields['description'].widget.attrs['rows'] = 5
        # Add field to select from previous user trips, if relevant
        if user and place:
            self.fields['user_trips'] = forms.ChoiceField(
                required = False,
                choices = [
                    (trip.id, trip.title())
                    for trip in user.created_trip_set.all().filter(
                        place = place
                    )
                ]
            )
            self.fields.keyOrder = self.Meta.fields + ('user_trips',)

    class Meta:
        model = Trip
        fields = (
            # Do start_accuracy before start so that when we adjust it in 
            # clean_start it doesn't get wiped over by its own (implicit) 
            # clean processing
            'start_accuracy', 'start', 'name', 'description', 'rating', 
        )

    def clean_start(self):
        start = self.cleaned_data['start'].lower()
        if start == '':
            self.cleaned_data['start_accuracy'] = 'day'
            return None

        m = re.match('\s*(\d{4})\s*$', start)
        if m:
            self.cleaned_data['start_accuracy'] = 'year'
            return datetime.date(int(m.group(1)), 1, 1)

        re_val = Calendar().ptc.re_values
        re_val['sep'] = '[\s/,.-]+'
        re_val['month_bit'] = '(%(months)s|%(shortmonths)s|\d\d?)' % re_val

        month_match = re.match('\s*(?P<month>%(month_bit)s)\s*$' % re_val, start)
        if month_match:
            month = month_match.group('month')
            month = int(Calendar().ptc.MonthOffsets.get(month, month))
            self.cleaned_data['start_accuracy'] = 'month'
            return datetime.date(datetime.date.today().year, month, 1)

        month_match = re.match('\s*((?P<month>%(month_bit)s)%(sep)s(?P<year>\d{4})|(?P<year2>\d{4})%(sep)s(?P<month2>%(month_bit)s))\s*$' % re_val, start)
        if month_match:
            year = month_match.group('year') or month_match.group('year2')
            month = month_match.group('month') or month_match.group('month2')
            month = int(Calendar().ptc.MonthOffsets.get(month, month))
            self.cleaned_data['start_accuracy'] = 'month'
            return datetime.date(int(year), month, 1)

        day_match = re.match('\s*((?P<day>\d\d?)(%(daysuffix)s)?%(sep)s(?P<month>%(month_bit)s)%(sep)s(?P<year>\d{4})|(?P<year2>\d{4})%(sep)s(?P<month2>%(month_bit)s)%(sep)s(?P<day2>\d\d?)(%(daysuffix)s)?)\s*$' % re_val, start)
        if day_match:
            year = day_match.group('year') or day_match.group('year2')
            month = day_match.group('month') or day_match.group('month2')
            day = day_match.group('day') or day_match.group('day2')
            month = int(Calendar().ptc.MonthOffsets.get(month, month))
            self.cleaned_data['start_accuracy'] = 'day'
            return datetime.date(int(year), month, int(day))

        parse = Calendar().parse(start)
        if parse[1] == 0:
            raise forms.ValidationError("I'm afraid we couldn't parse that date; please try again.")

        self.cleaned_data['start_accuracy'] = 'day'
        # Bit of a hack
        if re.search('year', start):
            self.cleaned_data['start_accuracy'] = 'year'
        elif re.search('month', start):
            self.cleaned_data['start_accuracy'] = 'month'

        return datetime.date(*parse[0][:3])
