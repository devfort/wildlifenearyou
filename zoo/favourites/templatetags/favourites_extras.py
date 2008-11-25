from django import template

register = template.Library()

@register.inclusion_tag('tags/favourite_toggler.html')
def favourite_toggler(action, slug, next):
    return {'action': action,
            'slug': slug,
            'next': next}
