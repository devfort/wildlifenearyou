from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, \
    HttpResponseServerError
from django.utils import dateformat

from zoo.shortcuts import render
from zoo.places.models import Place, Country, PlaceOpening, PlaceSpeciesSolelyForLinking
from zoo.animals.models import Species
from zoo.trips.models import Trip, Sighting

SPECIES_ON_PLACE_PAGE = 10

def place(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)

    species_list = place.get_species(request.user, SPECIES_ON_PLACE_PAGE)

    opening_times = {}
    for opening in place.placeopening_set.all():

        start_date = opening.start_date or ''
        end_date = opening.end_date or ''

        if start_date and end_date:
            # now see if we need to add the end date
            if end_date > start_date:
                # now check if month and year are the same
                if dateformat.format(start_date, 'mY') == dateformat.format(end_date, 'mY'):
                    date_range = u'%s &mdash; %s' % (dateformat.format(start_date, 'jS'), dateformat.format(end_date, 'jS F Y'))
                elif start_date.year == end_date.year:
                    date_range = u'%s &mdash; %s' % (dateformat.format(start_date, 'jS F'), dateformat.format(end_date, 'jS F Y'))
                else:
                    date_range = u'%s &mdash; %s' % (date, dateformat.format(end_date, 'jS F Y'))
            else:
                date_range = u'%s' % start_date
        elif start_date:
            date_range = u'%s &mdash;' % dateformat.format(start_date, 'jS F Y')
        elif end_date:
            date_range = u'&mdash; %s' % dateformat.format(end_date, 'jS F Y')
        else:
            date_range = '';

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
        'rating' : Trip.get_average_rating(place),
    })

def place_summary(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)

    species_list = place.get_species(request.user)

    return render(request, 'places/place_summary.html', {
        'place': place,
        'species_list': species_list,
    },
                  base='base_print.html')

def place_species(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)

    species_list = place.get_species(request.user)

    return render(request, 'places/place_species.html', {
        'place': place,
        'species_list': species_list,
    })

def place_species_view(request, country_code, slug, species_slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)
    species = get_object_or_404(Species, slug=species_slug)
    place_species_list = PlaceSpeciesSolelyForLinking.objects.filter(place=place).filter(species=species)
    if len(place_species_list)==0:
        # auto-create here
        place_species = PlaceSpeciesSolelyForLinking(place=place, species=species)
        place_species.save()
    else:
        place_species = place_species_list[0]
    sighters = [s.created_by for s in Sighting.objects.filter(species=species).filter(place=place).all()]

    return render(request, 'places/place_species_view.html', {
    'place': place,
    'place_species': place_species,
    'species': species,
    'sighters': sighters,
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

from zoo.places.forms import PlaceUberForm
from zoo.changerequests.models import ChangeRequestGroup, ChangeAttributeRequest

def place_edit(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)

    if request.method == 'POST':
        uf = PlaceUberForm(place, request.POST)

        if uf.is_valid():
            print request.POST.keys()
            if 'save all' in request.POST.get('submit', '').lower():
                changes = uf.changes()
                if changes:
                    crg = ChangeRequestGroup.objects.create()

                    for (obj, attrname), (oldval, newval) in changes.iteritems():
                        ChangeAttributeRequest.objects.create(
                            group=crg,
                            content_object=obj,
                            attribute=attrname,
                            old_value=oldval,
                            new_value=newval,
                        )

        else:
            print "INVALID"
    else:
        uf = PlaceUberForm(place)

    return render(request, 'places/place_edit.html', {
        'place': place,
        'form': uf,
    })
