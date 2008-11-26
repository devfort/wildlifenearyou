from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, \
    HttpResponseServerError
from zoo.shortcuts import render

from zoo.places.models import Place, Country, EnclosureSpecies, Enclosure
from zoo.animals.models import Species
from zoo.trips.models import Trip, Sighting

SPECIES_ON_PLACE_PAGE = 10

def get_place_species(place, user, limit=None):
    passport = Trip.get_passport(user)

    by_count = {}
    for sighting in Sighting.objects.filter(place=place):
        species = sighting.species
        by_count[species] = by_count.get(species, 0) + 1

    if by_count.values():
        max_species = max(by_count.values())

    species_list = by_count.keys()
    for species in species_list:
        species.count = by_count[species]
        species.quad = int( 4 * ( by_count[species] - 1.0 ) / max_species )
        if species in passport.seen_species:
            species.seen = True

    species_list.sort(key=lambda s: s.common_name)

    if limit:
        species_list = species_list[:limit]

    return species_list

def place(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)

    species_list = get_place_species(place, request.user, SPECIES_ON_PLACE_PAGE)

    opening_times = {}
    for opening in place.placeopening_set.all():

        start_date = opening.start_date or ''
        end_date = opening.end_date or ''
        if start_date == end_date:
            date_range = "%s" % start_date
        else:
            date_range = "%s &mdash; %s" % (start_date, end_date)

        arr = opening_times.setdefault(date_range, {}).setdefault(opening.section, [None] * 8)

        def gen_day_dict(day_of_week=None):
            name = None
            if day_of_week is not None:
                name = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat')[day_of_week]

            return {
                'name': name,
                'times': opening.times,
                'closed': opening.closed,
            }

        if opening.days_of_week:
            days_of_week = opening.days_of_week.split(',')
            for d in days_of_week:
                arr[int(d)+1] = gen_day_dict(int(d))
        else:
            arr[0] = gen_day_dict()

    times_sorted = [ (key, opening_times[key]) for key in sorted(opening_times.keys()) ]

    return render(request, 'places/place.html', {
        'place': place,
        'species_list': species_list,
        'opening_times': times_sorted,
    })

def place_species(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)

    species_list = get_place_species(place, request.user)

    return render(request, 'places/place_species.html', {
        'place': place,
        'species_list': species_list,
    })

def all_places(request):
    return render(request, 'places/all_places.html', {
        'all_places': Place.objects.all().order_by('known_as'),
    })


def country(request, country_code):
    country = get_object_or_404(Country, country_code=country_code)
    places = Place.objects.filter(country__country_code=country_code).order_by('known_as')

    return render(request, 'places/country.html', {
        'country': country,
        'places': places,
    })

def all_countries(request):
    return render(request, 'places/all_countries.html', {
        'all_countries': Country.objects.all().order_by('name'),
    })

from zoo.places.forms import EnclosureSpeciesEditForm, EnclosureEditForm

def edit_enc_species(request, ea_id):
    ea = EnclosureSpecies.objects.get(pk=ea_id)

    from zoo.changerequests.models import ChangeAttributeRequest, ChangeRequestGroup

    if request.method == 'POST':
        form = EnclosureSpeciesEditForm(instance=ea,
                                       data=request.POST)
        if form.is_valid():
            changes = []

            for name, val in form.cleaned_data.items():
                oldval = getattr(form.instance, name)
                if oldval != val:
                    changes.append(ChangeAttributeRequest(content_object=ea,
                                                          attribute=name,
                                                          value=val))

            if changes:
                crg = ChangeRequestGroup.objects.create()
                for c in changes:
                    c.group = crg
                    c.save()
    else:
        form = EnclosureSpeciesEditForm(instance=ea)

    return render(request, "edit/ea.html", {
        'form': form,
        })

from pprint import pprint

class UberForm(object):
    def __init__(self, instance, data=None, prefix=""):
        if prefix != "":
            prefix += "__"
        prefix += '%s-%s' % (type(instance).__name__, instance.pk)

        kwargs = {
            'instance': instance,
            'prefix': prefix,
        }

        if data:
            kwargs['data'] = data

        from django import forms

        form_list = []

        for part in self.parts:
            if isinstance(part, type) and issubclass(part, forms.BaseForm):
                form_list.append(part(**kwargs))
            else:
                objects = part(instance)
                for obj in objects:
                    sub_uber_form_klass = UF_DEFS[type(obj)]

                    suf = sub_uber_form_klass(obj, data, prefix)
                    form_list.extend(suf.forms)

        self.forms = form_list

    model = None
    parts = []

class EnclosureUberForm(UberForm):
    model = Enclosure
    parts = [
        EnclosureEditForm,
        lambda instance: instance.enclosurespecies_set.all(),
        ]

class EnclosureSpeciesUberForm(UberForm):
    model = EnclosureSpecies
    parts = [
        EnclosureSpeciesEditForm,
        ]

UF_DEFS = {}
for uf in EnclosureUberForm, EnclosureSpeciesUberForm:
    UF_DEFS[uf.model] = uf

def edit_enc(request, enc_id):

    enclosure = get_object_or_404(Enclosure, pk=enc_id)

    if request.method == 'POST':
        uf = EnclosureUberForm(enclosure, request.POST)

        is_valid = True
        for form in uf.forms:
            if not form.is_valid():
                is_valid = false
                break

        if is_valid:
            print "all valid"

    else:
        uf = EnclosureUberForm(enclosure)

    return render(request, "edit/enc.html", {
        'forms': uf.forms,
    })
