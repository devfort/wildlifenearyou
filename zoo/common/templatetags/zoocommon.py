from django import template
register = template.Library()

@register.filter
def oncetimes(n):
    s = {
        0: 'zero times',
        1: 'once',
        2: 'twice',
        3: 'three times',
        4: 'four times',
        5: 'five times',
        6: 'six times',
        7: 'seven times',
        8: 'eight times',
        9: 'nine times',
    }.get(n)
    if not s:
        s = '%d times' % n
    return s
