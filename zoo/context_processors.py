from django.core.cache import cache
from zoo.animals.models import Species

def standard(request):
    num = cache.get('total_num_of_species')
    if not num:
        num = Species.objects.all().count()
        cache.set('total_num_of_species', num, 60)
    return {'base': 'base.html',
            'total_num_of_species': num}
