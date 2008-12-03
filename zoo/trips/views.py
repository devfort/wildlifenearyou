from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect as Redirect
from django.contrib.auth.decorators import login_required
from django import forms

import datetime, urllib
from parsedatetime.parsedatetime import Calendar

from zoo.shortcuts import render
from zoo.trips.models import Trip, Sighting, InexactSighting
from zoo.accounts.models import Profile
from zoo.animals.forms import SpeciesField
from zoo.search import NotFound, lookup_species, search_species

@login_required
def tripbook_default(request):
    return Redirect(reverse('tripbook', args=(request.user,)))

def tripbook(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'trips/tripbook.html', {
        'tripbook': user.created_trip_set.all(),
        'profile': user.get_profile(),
    })

def trip_view(request, username, trip_id):
    user = get_object_or_404(User, username=username)
    trip = get_object_or_404(Trip, id=trip_id, created_by=user)
    return render(request, 'trips/trip.html', {
        'profile': user.get_profile(),
        'trip': trip,
        # do this to prepare the rating for the view
        'rating': Trip.calculate_rating_average([trip]),
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
def pick_sightings_for_place(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)
    return pick_sightings(request, '/%s/%s/add-sightings/' % (
        country_code.lower(), slug
    ))

from django.utils.datastructures import DotExpandedDict

@login_required
def pick_sightings(request, redirect_to):
    """
    A replacement for the old add_sightings view. This one is designed to 
    sit in between two different parts of the interface. It narrows down
    the list of entered text to concrete species as before, then forwards 
    the user on to the redirect_to URL with concrete species IDs attached.
    
    For example, the resulting redirect may look like this:
    
    /gb/london-zoo/add-trip/?saw=x:2ab1&saw=s:123&saw=A+baby+tiger
    
    Note that there are now three types of saw IDs:
    
       x:* = a Xapian search ID
       s:* = an animals_species table ID
       *   = free text not matched in our database
    
    Our sightings recording mechanism is now expected to be able to deal with 
    free text, which will be turned in to an InexactSighting record.
    
    The INPUT to this view should start off as something like this:
    
    ../pick-sightings/?saw.1.s=tiger&saw.2.s=pony
    
    If there are any ?saw= items, the view redirects straight away turning
    them in to that format. So, the easiest way to get started with the 
    process is to send someone to:
    
    ../pick-sightings/?saw=tiger&saw=pony
    
    If called with no arguments, starts off with an empty "I saw" form
    
    """
    if request.GET.getlist('saw'):
        # Convert ?saw= arguments to ?saw.1.s= type things
        return Redirect(request.path + '?' + urllib.urlencode([
            ('saw.%d.s' % i, saw.strip())
            for i, saw in enumerate(request.GET.getlist('saw'))
            if saw.strip()
        ]))
    
    saw = DotExpandedDict(request.GET).get('saw')
    if request.GET and not saw:
        # Clear out the invalid query string
        return Redirect(request.path)
    
    if not saw:
        assert False, "Jump straight to showing the empty form"
    
    # saw should now of format {'0': {'s': 'tiger', 'o': 'x:ba3'}...}
    # Essentially a dictionary of key/dict pairs. The key doesn't actually 
    # matter, it's just used to group values. The dict looks like this:
    #     s = The text the user entered (required)
    #     o = The option they picked to fulfill it (optional)
    #     r = The replacement search they want to run (defaults to same as s)
    # The 'o' value comes from a radio select and can be of these formats:
    #     x_*    = a Xapian search ID they have selected
    #     s_*    = a Species ID they have selected
    #     cancel = don't save this at all (e.g. "I made a mistake")
    #     as-is  = save it as a InexactSighting record
    #     search-again = run the replacement search instead
    
    # Are we done yet? The aim is for every key to have a valid option 
    # provided that isn't 'search-again'.
    if saw and is_valid_saw_list(saw.values()):
        return Redirect(redirect_to + '?' + '&'.join([
            urllib.urlencode({
                'saw': d['o'] == 'as-is' and d.get('s') or d['o']
            })
            for d in saw.values()
            if d.get('s') and (d['o'] != 'cancel')
        ]))
    
    # We aren't done, so we need to build up all of the information required
    # to construct our big form full of options, search results etc
    sections = []
    
    section_id = 0
    label_id = 0
    if saw:
        for key in sorted(saw.keys(), key = lambda k: int(k)):
            d = saw[key]
            search = d.get('r', d['s']).strip()
            if not search:
                continue
            results = list(search_species(search, 20))
            db_matches = list(Species.objects.filter(freebase_id__in = [
                r['freebase_id'] for r in results
            ]))
            choices = []
            is_first = True
            for row in results:
                try:
                    id = 's_%s' % [
                        s for s in db_matches 
                        if s.freebase_id == r['freebase_id']
                    ][0].id
                except IndexError:
                    id = 'x_%s' % r['search_id']
                choices.append({
                    'id': id,
                    'common_name': row['common_name'],
                    'scientific_name': row['scientific_name'],
                    'label_id': label_id,
                    'checked': (d.get('o') == id or (
                        is_first and d.get('o') != 'cancel'
                    )),
                })
                label_id += 1
                is_first = False
            
            sections.append({
                'id': section_id,
                'search': d.get('r', d['s']), # Pick up replacement search
                'options': choices,
                'o': d.get('o'),
            })
            section_id += 1
    
    return render(request, 'trips/pick_sightings.html', {
        'sections': sections,
        'redirect_to': redirect_to,
        'bonus_label_id': section_id,
    })

def is_valid_saw_list(saw_list):
    "Returns True if every 's' has a corresponding, valid 'o'"
    for d in saw_list:
        if not d.get('s').strip():
            continue
        o = d.get('o')
        if not o:
            return False
        if o == 'search-again':
            return False
    return True

@login_required
def finish_add_sightings_to_place(request, country_code, slug):
    """
    At this point, the user has told us exactly what they saw. We're going to
    add those as sightings, but first, let's see if we can get them to add 
    a full trip (which has a date or a title or both, and a optional 
    description for their tripbook).
    """
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)
    saw_id_set = set(request.REQUEST.getlist('saw'))
    hiddens = []
    for i, saw_id in enumerate(saw_id_set):
        hiddens.append(
            {'name': 'saw', 'value': saw_id}
        )
    # Text descriptions of sightings, so we can display them to the user
    sightings = []
    for saw_id in saw_id_set:
        species = lookup_xapian_or_django_id(saw_id)
        if species:
            sightings.append(species)
        else:
            sightings.append(saw_id)
    
    if request.method == 'POST':
        if request.POST.get('just-sightings'):
            for id in saw_id_set:
                # Look up the id
                species = lookup_xapian_or_django_id(id)
                if species: # None if it was somehow invalid
                    Sighting.objects.create(
                        species = species,
                        place = place
                    )
                else:
                    InexactSighting.objects.create(
                        species = id,
                        place = place
                    )
            return Redirect(place.get_absolute_url())
        
        form = FinishAddSightingsForm(request.POST, user=request.user, place=place)
        if form.is_valid():
            if request.POST.get('add-to-existing'):
                # if the user chose this option they want to add this sighting to an existing trip of theirs
                trip = Trip.objects.get(id=form.cleaned_data['user_trips'])
            else:
                # create a new trip
                trip = Trip(
                    name = form.cleaned_data['name'],
                    start = form.cleaned_data['start'],
                    start_accuracy = form.cleaned_data['start_accuracy'],
                    description = form.cleaned_data['description'],
                    rating = form.cleaned_data['review-rating'],
                )
                trip.save()
                # created_by should happen automatically
            
            # Now we finally add the sightings!
            for id in saw_id_set:
                # Look up the id
                species = lookup_xapian_or_django_id(id)
                if species: # None if it wasn't a valid ID
                    trip.sightings.create(
                        species = species,
                        place = place,
                    )
                else:
                    # Invalid IDs are InexactSightings, add them as such
                    trip.inexact_sightings.create(
                        place = place,
                        species = id,
                    )
                # TODO: Shouldn't allow a trip to be added if no valid 
                # sightings
            
            return Redirect(trip.get_absolute_url())
        
    else:
        # We pre-populate the name
        if not request.user.first_name:
            whos_trip = 'My'
        else:
            whos_trip = request.user.first_name
            if whos_trip.endswith('s'):
                whos_trip += "'"
            else:
                whos_trip += "'s"
        whos_trip += ' trip'
        form = FinishAddSightingsForm(initial = {'name': whos_trip}, user=request.user, place=place)
        
    tcount = request.user.created_trip_set.all().filter(sightings__place=place).distinct().count()
    
    return render(request, 'trips/why-not-add-to-your-tripbook.html', {
        'hiddens': hiddens,
        'place': place,
        'form': form,
        'tcount': tcount,
        'sightings': sightings,
    })

class FinishAddSightingsForm(forms.Form):
    name = forms.CharField(max_length=100, label='Trip title')
    start = forms.CharField(required = False, label='Trip date')
    description = forms.CharField(required = False, widget=forms.Textarea,
        label='Notes'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        place = kwargs.pop('place')
        trips = user.created_trip_set.all().filter(sightings__place=place).distinct()

        super(FinishAddSightingsForm, self).__init__(*args, **kwargs)
        self.fields['review-rating'] = forms.ChoiceField(required = False, choices=[ (i,i) for i in range(1,6) ])
        self.fields['user_trips'] = forms.ChoiceField(required = False, choices=[ (trip.id, trip.title()) for trip in trips ]) 

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

def lookup_xapian_or_django_id(id):
    if id.startswith('s_'):
        id = id[2:]
        try:
            return Species.objects.get(pk = id)
        except Species.DoesNotExist:
            return None
    elif id.startswith('x_'):
        id = id[2:]
        # Look it up in Xapian
        try:
            details = lookup_species(id)
        except NotFound:
            return None
        # If it's a Django object already, return that
        try:
            return Species.objects.get(freebase_id = details['freebase_id'])
        except Species.DoesNotExist:
            # Save it to the database
            obj, created = Species.objects.get_or_create(
                slug = details['common_name'].replace(' ', '-').lower(),
                common_name = details['common_name'],
                latin_name = details['scientific_name'],
                freebase_id = details['freebase_id'],
            )
            return obj
    else:
        return None
