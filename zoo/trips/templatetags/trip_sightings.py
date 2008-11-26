from django import template

register = template.Library()

@register.inclusion_tag('trips/_trip_sightings.html')
def trip_sightings(trip):
    return { 'trip': trip, }
