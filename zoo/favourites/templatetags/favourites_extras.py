from django import template

register = template.Library()

@register.inclusion_tag('tags/favourite_toggler.html')
def favourite_toggler(action, slug, next, klass='', add_label='Add to favourites', remove_label='Remove from favourites'):
    return {'action': action,
            'slug': slug,
            'next': next,
            'class': klass,
            'add_label': add_label,
            'remove_label': remove_label,}
