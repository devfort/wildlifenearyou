from django.db import models
from animals.models import Species
import redis

SPECIES_SET = 'species-with-multiple-photos'

def random_species_with_multiple_photos():
    #return Species.objects.get(common_name__contains = 'eerkat')
    r = redis.Redis()
    while True:
        pk = r.srandmember(SPECIES_SET)
        if not pk:
            raise ValueError, 'No species with multiple photos available'
        try:
            return Species.objects.get(pk = pk)
        except Species.DoesNotExist:
            r.srem(SPECIES_SET, pk)

def update_redis_set():
    r = redis.Redis()
    r.delete(SPECIES_SET + '-temp')
    species_with_multiple_photos = Species.objects.filter(
        sightings__photos__is_visible = True
    ).annotate(                  
        num_photos = models.Count('sightings__photos')
    ).filter(num_photos__gt = 1)
    
    for pk in species_with_multiple_photos.values_list('pk', flat = True):
        r.sadd(SPECIES_SET + '-temp', pk)
    
    r.rename(SPECIES_SET + '-temp', SPECIES_SET)

def record_win(species, winner, loser):
    r = redis.Redis()
    # We record the win-percentage for everything - what percentage of 
    # competitions it has been in has it won? We do this on a per-species 
    # basis to account for photos with multiple species that are great for 
    # one and bad for the other.
    winner_times_seen = r.incr('bestpics-photo-times-seen:%s' % winner)
    loser_times_seen = r.incr('bestpics-photo-times-seen:%s' % loser)
    winner_times_won = r.incr('bestpics-photo-times-won:%s' % winner)
    loser_times_won = r.get('bestpics-photo-times-won:%s' % loser) or 0
    
    winner_score = (
        float(winner_times_won) / float(winner_times_seen)
    )
    loser_score = (
        float(loser_times_won) / float(loser_times_seen)
    )
    
    # Update scores in the ordered set
    r.zadd('bestpics-species:%s' % species, winner, winner_score)
    r.zadd('bestpics-species:%s' % species, loser, loser_score)
    
    return {
        'winner_times_seen': winner_times_seen,
        'winner_times_won': winner_times_won,
        'winner_score': winner_score,
        'loser_times_seen': loser_times_seen,
        'loser_times_won': loser_times_won,
        'loser_score': loser_score,
    }
