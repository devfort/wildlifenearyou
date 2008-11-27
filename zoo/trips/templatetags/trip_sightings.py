from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.inclusion_tag('trips/_trip_sightings.html')
def trip_sightings(trip, htag, htag2, link_title):
    return { 'trip': trip,
             'htag': htag,
             'htag2': htag2,
             'link_title': link_title }
