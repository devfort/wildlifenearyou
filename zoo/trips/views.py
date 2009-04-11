from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect as Redirect
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import DotExpandedDict
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
    if user == request.user:
        photos = trip.photos.all()
    else:
        photos = trip.visible_photos()
    return render(request, 'trips/trip.html', {
        'profile': user.get_profile(),
        'trip': trip,
        # do this to prepare the rating for the view
        'rating': Trip.calculate_rating_object([trip]),
        'belongs_to_user': request.user.id == user.id,
        'visible_photos': photos,
    })

@login_required
def pick_sightings_for_place(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)
    return pick_sightings(request, '/%s/%s/add-sightings/' % (
        country_code.lower(), slug
    ))

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
    free text, which will be recorded using species_inexact on a Sighting.
    
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
    #     as-is  = save it using species_inexact
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
                        if s.freebase_id == row['freebase_id']
                    ][0].id
                except IndexError:
                    id = 'x_%s' % row['search_id']
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
    saw_ids = request.REQUEST.getlist('saw')
    hiddens = []
    for saw_id in saw_ids:
        hiddens.append(
            {'name': 'saw', 'value': saw_id}
        )
    # Text descriptions of sightings, so we can display them to the user
    sightings = []
    for saw_id in saw_ids:
        species = lookup_xapian_or_django_id(saw_id)
        if species:
            sightings.append(species)
        else:
            sightings.append(saw_id)
    
    if request.method == 'POST':
        if request.POST.get('just-sightings'):
            for i, id in enumerate(saw_ids):
                # Look up the id
                species = lookup_xapian_or_django_id(id)
                note = request.POST.get('sighting_note_%d' % i, '')
                if species: # None if it was somehow invalid
                    Sighting.objects.create(
                        species = species,
                        place = place,
                        note = note
                    )
                else:
                    Sighting.objects.create(
                        species_inexact = id,
                        place = place,
                        note = note
                    )
            return Redirect(place.get_absolute_url())
        
        form = AddTripForm(request.POST, initial = {'place': place})
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
                    rating = form.cleaned_data['rating'],
                    place = place,
                )
                trip.save()
                # created_by should happen automatically
            
            # Now we finally add the sightings!
            for i, id in enumerate(saw_ids):
                # Look up the id
                species = lookup_xapian_or_django_id(id)
                note = request.POST.get('sighting_note_%d' % i, '')
                if species: # None if it wasn't a valid ID
                    trip.sightings.create(
                        species = species,
                        place = place,
                        note = note,
                    )
                else:
                    # Invalid IDs are inexact sightings, add them as such
                    trip.sightings.create(
                        place = place,
                        species_inexact = id,
                        note = note,
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
        form = AddTripForm(initial = {'name': whos_trip, 'place': place})

    tcount = request.user.created_trip_set.all().filter(place=place).count()
    
    return render(request, 'trips/why-not-add-to-your-tripbook.html', {
        'hiddens': hiddens,
        'place': place,
        'form': form,
        'tcount': tcount,
        'sightings': sightings,
    })

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ('name', 'start', 'start_accuracy', 'description', 'rating')
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.place = kwargs.pop('place')
        super(TripForm, self).__init__(*args, **kwargs)
        self.fields['rating'] = forms.ChoiceField(
            required = False,
            choices = [(i,i) for i in range(1,6)]
        )
    
    def save(self):
        obj = super(TripForm, self).save(commit = False)
        obj['created_by'] = self.user
        obj['place'] = self.place
        return obj.save()

class FinishAddSightingsForm(forms.Form):
    name = forms.CharField(max_length=100, label='Trip title')

class AddTripForm(forms.ModelForm):
    # In the model this is a date, but we do some magic to allow more flexibility (see clean_start below).
    start = forms.CharField(required = False, label='Trip date')
    # And this has to be there or it won't be saved
    start_accuracy = forms.CharField(required = False, label='Start accuracy (hidden)')
    # Override the default for this, since we need it to match the widget we're using
    rating = forms.ChoiceField(required = False, choices=[ (i,i) for i in range(1,6) ])

    def __init__(self, *args, **kwargs):
        super(AddTripForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Trip title'
        self.fields['description'].label = 'Notes'
        self.fields.keyOrder = self.Meta.fields

    class Meta:
        model = Trip
        fields = (
            # Do start_accuracy before start so that when we adjust it in clean_start
            # it doesn't get wiped over by its own (implicit) clean processing
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

@login_required
def trip_delete(request, username, trip_id):
    user = get_object_or_404(User, username=username)
    trip = get_object_or_404(Trip, id=trip_id, created_by=user)
    assert request.user.id == user.id, "You can only delete your own trips!"
    if request.POST.get('confirm_delete'):
        # Delete the sightings for the trip
        for sighting in list(trip.sightings.all()):
            # First, unlink any photos attached to this sighting
            for photo in list(sighting.photos.all()):
                photo.sighting = None
                photo.trip = None
                photo.save()
            sighting.delete()
        
        # Delete the trip
        place = trip.place
        trip.delete()
        place.save() # Re-index to update denormalised stuff
        
        return Redirect(reverse('accounts-profile', args=(username,)))
    
    return render(request, 'trips/trip_delete.html', {
        'trip': trip,
    })

class EditTripForm(AddTripForm):
    def __init__(self, *args, **kwargs):
        super(EditTripForm, self).__init__(*args, **kwargs)
        if kwargs['instance']:
            # This feels wrong. But it works.
            self.initial['start'] = kwargs['instance'].formatted_start_date()

from django.forms.models import inlineformset_factory
SightingFormSet = inlineformset_factory(
    parent_model = Trip,
    model = Sighting,
    fields = ('note',),
    extra = 0
)

@login_required
def edit_trip(request, username, trip_id):
    user = get_object_or_404(User, username=username)
    trip = get_object_or_404(Trip, id=trip_id, created_by=user)
    if request.user.id != user.id:
        return HttpResponseForbidden()

    if request.method=='POST':
        form = EditTripForm(request.POST, instance=trip)
        sightings_formset = SightingFormSet(request.POST, instance=trip)
        
        if form.is_valid() and sightings_formset.is_valid():
            dates_match = False
            if trip.end == trip.start:
                dates_match = True
            trip2 = form.save(commit = False)
            if trip2.end == trip.end and dates_match:
                # Preserve matching start/end dates unless the end date has 
                # been explicitly changed (which won't happen at the moment as 
                # we don't offer it in the interface)
                trip2.end = trip.start
            trip2.save()
            sightings_formset.save()
            return Redirect(reverse('trip-view', args=(username, trip_id,)))
    else:
        form = EditTripForm(instance=trip)
        sightings_formset = SightingFormSet(instance = trip)
    
    return render(request, 'trips/trip_edit.html', {
        'trip': trip,
        'form': form,
        'sightings_formset': sightings_formset,
    })

@login_required
def add_trip_select_place(request):
    """
    If a user opts to "add a trip" without starting on a place page, we first 
    need to determine where the trip took place. We offer users a search 
    form for this. If they search and STILL can't find the place they went 
    to, we allow them to add a brand new place to our database. This place 
    will not be marked as "approved" until a member of site staff has 
    approved it. Unapproved places do not show up in browse or global search 
    and are not linked to from anywhere other than the user's own trip page.
    They DO show up in this particular search form though, but ranked lower 
    than matches that are approved.
    """
    q = request.GET.get('q', '')
    if not q:
        return render(request, 'trips/add_trip_select_place.html')
    
    # TODO: use the search engine for this
    places = Place.objects.filter(known_as__icontains = q)
    
    suggested_title = q
    if not re.search('[A-Z]', suggested_title):
        suggested_title = suggested_title.title()
    
    return render(request, 'trips/add_trip_select_place_results.html', {
        'q': q,
        'places': places,
        'form': AddPlaceForm(initial={'known_as': suggested_title}),
    })

@login_required
def add_trip_add_place(request):
    if request.method == 'POST':
        form = AddPlaceForm(request.POST)
        if form.is_valid():
            place = form.save(commit = False)
            if not place.legal_name:
                place.legal_name = place.known_as
            place.is_confirmed = False
            # Derive an unused slug
            append = 1
            first_slug = slugify(place.known_as)
            slug = first_slug
            while Place.objects.filter(slug = slug).count():
                slug = '%s-%d' % (first_slug, append)
                append += 1
            place.slug = slug
            place.save()
            return Redirect(place.get_absolute_url() + 'add-trip/')
    else:
        form = AddPlaceForm()
    return render(request, 'trips/add_trip_add_place.html', {
        'form': form,
    })

@login_required
def add_trip(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)
    return render(request, 'trips/add_trip.html', {
        'place': place,
    })

class AddPlaceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddPlaceForm, self).__init__(*args, **kwargs)
        self.fields['known_as'].label = 'Place name'
        self.fields['known_as'].widget.attrs['size'] = 50
        self.fields['url'].label = 'URL'
        self.fields['zip'].label = 'Postal code / ZIP'
        for key in ('address_line_1', 'address_line_2'):
            self.fields[key].widget.attrs['size'] = 30
        self.fields.keyOrder = self.Meta.fields
    
    class Meta:
        model = Place
        fields = (
            'known_as', 'country', 'url', 'address_line_1', 'address_line_2', 
            'town', 'state', 'zip', 'phone', 'latitude', 'longitude',
        )

from zoo.search import search_species
def autocomplete_species(request, place_id):
    place = get_object_or_404(Place, pk = place_id)
    q = request.GET.get('q', '')
    results = list(search_species(q))
    # We're going to build three groups - species that have been sighted at 
    # this place, species that have been sighted somewhere else, and species 
    # that have not been sighted at all.
    seen_here_group = []
    seen_elsewhere_group = []
    not_seen_group = []
    for result in results:
        # If it's in our Species database, annotate with a bunch of stuff
        species = None
        try:
            species = Species.objects.get(freebase_id = result['freebase_id'])
        except Species.DoesNotExist:
            pass
        if not species:
            result['select_id'] = 'x_%s' % result['search_id']
            not_seen_group.append(result)
            continue
        # Matches a known species
        result['select_id'] = 's_%s' % species.id
        # Annotate with photo
        photos = Photo.objects.filter(
            sightings__species = species,
            is_visible = True
        ).distinct()
        result['photo'] = photos and unicode(photos[0].photo.thumbnail) or ''
        # Assign to a group and annotate with number of previous sightings
        num_sightings_here = Sighting.objects.filter(
            species = species,
            place = place
        ).count()
        if num_sightings_here:
            result['num_sightings'] = num_sightings_here
            seen_here_group.append(result)
            continue
        num_sightings = Sighting.objects.filter(
            species__freebase_id = result['freebase_id']
        ).count()
        if num_sightings:
            result['num_sightings'] = num_sightings
            seen_elsewhere_group.append(result)
            continue
        # Not seen anywhere before
        not_seen_group.append(result)
    
    # Order each group by number of sightings, with most at the top
    seen_here_group.sort(key = lambda r: r['num_sightings'], reverse=True)
    seen_elsewhere_group.sort(key = lambda r: r['num_sightings'], reverse=True)
    return render(request, 'trips/autocomplete_species.html', {
        'seen_here': seen_here_group,
        'seen_elsewhere': seen_elsewhere_group,
        'not_seen': not_seen_group,
        'q': q,
    })
