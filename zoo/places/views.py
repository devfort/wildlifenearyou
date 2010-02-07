from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, \
    HttpResponseServerError
from django.utils import dateformat

from zoo.shortcuts import render
from zoo.places.models import Place, Country, PlaceOpening, \
    PlaceSpeciesSolelyForLinking, PlaceCategory
from zoo.animals.models import Species
from zoo.trips.models import Trip, Sighting
from django.db.models import Count

SPECIES_ON_PLACE_PAGE = 10

# Given an array of days of the week, create a human-readable representation
def prettify_days(daynums):
    days_of_week = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat')
    in_range = False
    ranges = {}
    for d in range(7):
        if d in daynums and not in_range:
            in_range = True
            range_start = d
        if d not in daynums and in_range:
            in_range = False
            ranges[range_start] = d-1
    if in_range:
            if 0 in ranges:
                ranges[range_start] = ranges[0]
                del ranges[0]
            else:
                ranges[range_start] = d

    out = []
    for start in sorted(ranges):
        end = ranges[start]
        if start == end:
            out.append( days_of_week[start] )
        else:
            out.append( u"%s\u2013%s" % (days_of_week[start], days_of_week[end] ) )
       
    return ', '.join(out)

def get_times_sorted(place):
    # Loop through opening times in database, grouping by date range and section - only store one opening time per day to allow overriding
    opening_times = {}
    for opening in place.placeopening_set.all():

        start_date = opening.start_date or ''
        end_date = opening.end_date or ''
        date_range_machine = u"%s\u2013%s" % (start_date, end_date)

        # Create a human-readable date range
        if start_date and end_date:
            # now see if we need to add the end date
            if end_date > start_date:
                # now check if month and year are the same
                if dateformat.format(start_date, 'mY') == dateformat.format(end_date, 'mY'):
                    date_range = u"%s\u2013%s" % (dateformat.format(start_date, 'jS'), dateformat.format(end_date, 'jS F Y'))
                elif start_date.year == end_date.year:
                    date_range = u"%s\u2013%s" % (dateformat.format(start_date, 'jS F'), dateformat.format(end_date, 'jS F Y'))
                else:
                    date_range = u"%s\u2013%s" % (dateformat.format(start_date, 'jS F Y'), dateformat.format(end_date, 'jS F Y'))
            else:
                date_range = u'%s' % dateformat.format(start_date, 'jS F Y')
        elif start_date:
            date_range = u"%s\u2013" % dateformat.format(start_date, 'jS F Y')
        elif end_date:
            date_range = u"\u2013%s" % dateformat.format(end_date, 'jS F Y')
        else:
            date_range = '';

        if date_range_machine not in opening_times:
            opening_times[date_range_machine] = {
                'date_range': date_range,
                'sections': {},
                'single_date': (start_date and end_date and start_date == end_date),
            }

        # 8 element array, as index 7 is for the common "Every day" entry
        arr = opening_times[date_range_machine]['sections'].setdefault(opening.section, [None] * 8)

        opening_status = { 'times': opening.times, 'closed': opening.closed }
        if opening.days_of_week:
            days_of_week = opening.days_of_week.split(',')
            for d in days_of_week:
                arr[int(d)] = opening_status
        elif opening_times[date_range_machine]['single_date']:
            arr[7] = opening_status
        else:
            opening_status['name'] = 'Every day'
            arr[7] = opening_status

    # Now concatenate together days that have the same times
    for data in opening_times.values():
        for section, days in data['sections'].items():
            arr = []
            if days[7]:
                arr.append(days[7]) # First put any "Every day" entry
            for d in (1,2,3,4,5,6,0): # Week starts on Monday
                if days[d]:
                    daynums = [d]
                    for i in range(6):
                        if days[(d+i+1)%7] == days[d]:
                            daynums.append((d+i+1)%7)
                            days[(d+i+1)%7] = None
                    days[d]['name'] = prettify_days(daynums)
                    arr.append ( days[d] )
            data['sections'][section] = arr

    times_sorted = [ { 'range': opening_times[key]['date_range'], 'sections': opening_times[key]['sections'] } for key in sorted(opening_times) ]
    return times_sorted

def place(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)

    species_list = place.get_species(request.user, SPECIES_ON_PLACE_PAGE + 1)
    times_sorted = get_times_sorted(place)

    return render(request, 'places/place.html', {
        'place': place,
        'species_list': species_list[0:SPECIES_ON_PLACE_PAGE],
        'species_list_more': len(species_list) > SPECIES_ON_PLACE_PAGE,
        'opening_times': times_sorted,
        'rating' : Trip.get_average_rating(place),
        'been_here': Trip.objects.filter(
            place = place, created_by = request.user
        ).count(),
        'places_nearby': place.nearby.filter(
            place__is_unlisted = False
        ).select_related(
            'place', 'place__country'
        )[:3],
    })

def place_summary(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)
    
    times_sorted = get_times_sorted(place)
    
    return render(request, 'places/place_summary.html', {
        'place': place,
        'opening_times': times_sorted,
    }, base='base_print.html')

def place_animal_checklist(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)
    
    species_list = place.get_species(request.user)
    
    return render(request, 'places/place_animal_checklist.html', {
        'place': place,
        'species_list': species_list,
    }, base='base_print.html')

def place_photos(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)
    
    return render(request, 'photos/place_photos.html', {
        'place': place,
        'photos': place.visible_photos(),
    })

def place_species(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)

    species_list = place.get_species(request.user)

    return render(request, 'places/place_species.html', {
        'place': place,
        'species_list': species_list,
    })

def place_species_view(request, country, place, species):
    country = get_object_or_404(Country, country_code=country)
    place = get_object_or_404(Place, slug=place, country=country)
    species = get_object_or_404(Species, slug=species)
    place_species_list = PlaceSpeciesSolelyForLinking.objects.filter(
        place=place
    ).filter(species=species)
    if len(place_species_list)==0:
        # auto-create here
        place_species = PlaceSpeciesSolelyForLinking(
            place=place, species=species
        )
        place_species.save()
    else:
        place_species = place_species_list[0]

    sightings = Sighting.objects.filter(
        species=species
    ).filter(place=place)

    return render(request, 'places/place_species_view.html', {
        'place': place,
        'place_species': place_species,
        'species': species,
        'sightings': sightings,
    })

def all_places(request):
    return render(request, 'places/all_places.html', {
        'all_places': Place.objects.all().order_by('known_as'),
    })

def country(request, country_code):
    country = get_object_or_404(Country, country_code=country_code)
    places = Place.objects.filter(
        country = country,
        is_unlisted = False,
    ).order_by('known_as')
    categories = PlaceCategory.objects.filter(
        places__country = country,
        places__is_unlisted = False,
    ).annotate(num_places = Count('places'))
    return render(request, 'places/country.html', {
        'country': country,
        'places': places,
        'categories': categories,
        'uncategorised': Place.objects.filter(
            country = country,
            categories__isnull = True,
            is_unlisted = False,
        ).count(),
    })

def country_by_category(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    if slug == 'uncategorised':
        category = None
        category_name = 'Uncategorised places'
        places = Place.objects.filter(
            country = country,
            categories__isnull = True,
            is_unlisted = False,
        )
    else:
        category = get_object_or_404(PlaceCategory, slug = slug)
        category_name = category.plural or category.name
        places = Place.objects.filter(
            country = country,
            categories = category,
            is_unlisted = False,
        ).order_by('known_as')
    
    categories = PlaceCategory.objects.filter(
        places__country = country,
        places__is_unlisted = False,
    ).annotate(num_places = Count('places'))
    
    return render(request, 'places/country_by_category.html', {
        'country': country,
        'places': places,
        'categories': categories,
        'category': category,
        'category_name': category_name,
        'uncategorised': Place.objects.filter(
            country = country,
            categories__isnull = True,
            is_unlisted = False,
        ).count(),
    })

def all_countries(request):
    return render(request, 'places/all_countries.html', {
        'all_countries': Country.objects.all().annotate(
            num_places = Count('place'),
        ).order_by('-num_places'),
    })

from zoo.places.forms import PlaceUberForm
from zoo.changerequests.models import ChangeRequestGroup, \
     ChangeAttributeRequest, CreateObjectRequest

def place_edit(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)

    from django.contrib.contenttypes.models import ContentType

    if request.method == 'POST':
        uf = PlaceUberForm(place, request.POST)

        if uf.is_valid():
            if 'suggest all' in request.POST.get('submit', '').lower():
                changes, deletions = uf.modifications()

                crg = [None]
                def get_or_create_group():
                    # bad scoping! no binding.
                    if crg[0] is None:
                        crg[0] = ChangeRequestGroup.objects.create()
                    return crg[0]

                if changes:
                    for (obj, attrname), (oldval, newval) in changes.iteritems():
                        ChangeAttributeRequest.objects.create(
                            group=get_or_create_group(),
                            content_object=obj,
                            attribute=attrname,
                            old_value=oldval,
                            new_value=newval,
                        )

                def create_add_request(uf, data, parent_ret):
                    if uf.parent_uform:
                        #    'place'        Place object
                        data[uf.relation] = uf.parent_uform.instance.id

                        ct = ContentType.objects.get_for_model(uf.model)
                        group = get_or_create_group()
                        cor = CreateObjectRequest.objects.create(
                            group=group,
                            attributes=data,
                            parent=parent_ret,
                            reverse_relation=uf.relation or '',
                            content_type=ct,
                        )

                        return cor
                uf.mapadds(create_add_request)

                return HttpResponseRedirect(place.urls.changes_suggested)
    else:
        uf = PlaceUberForm(place)

    return render(request, 'places/place_edit.html', {
        'place': place,
        'form': uf,
    })

def place_edit_done(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)

    return render(request, 'places/place_edit_done.html', {
        'place': place,
        })

def support(request, country_code, slug):
    country = get_object_or_404(Country, country_code=country_code)
    place = get_object_or_404(Place, slug=slug, country=country)

    return render(request, 'places/place_support.html', {
        'place': place,
        })
