from django.core.management.base import BaseCommand, CommandError

from geopy import distance
from zoo.places.models import Place, DistanceBetween

def dist(p1, p2):
    try:
        return distance.VincentyDistance(
            (p1.latitude, p1.longitude), (p2.latitude, p2.longitude)
        ).km
    except ValueError: # 'Vincenty formula failed to converge!'
        return distance.GreatCircleDistance(
            (p1.latitude, p1.longitude), (p2.latitude, p2.longitude)
        ).km
    # Example input that causes Vincenty to fail to converge:
    # (14.058324000000001, 108.277199), (-13.1639038224, -72.545986175500005)

class Command(BaseCommand):
    help = """
    Populate the DistanceBetween table, so we know which places are nearby.
    """.strip()
    
    requires_model_validation = True
    can_import_settings = True
    
    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        all_places = list(Place.objects.all())
        
        def populate_nearby(place, distance=50):
            nearby = []
            for p in all_places:
                if p == place:
                    continue
                d = dist(p, place)
                if d <= distance:
                    nearby.append((p, d))
            DistanceBetween.objects.filter(origin = place).delete()
            for p, d in nearby:
                DistanceBetween.objects.create(
                    origin = place,
                    place = p,
                    distance_km = d,
                )
        
        for place in all_places:
            populate_nearby(place)
            print "Done %s, has %s within 50km" % (
                place, place.nearby.count()
            )
