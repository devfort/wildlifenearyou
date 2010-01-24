from django.db import models
from animals.models import Species
from photos.models import Photo
from redis_db import r
import random, uuid, datetime

SPECIES_SET = 'species-with-multiple-photos'
SEEN_KEY = 'bestpics-photo-times-seen:%s'
WON_KEY = 'bestpics-photo-times-won:%s'
BESTPICS_KEY = 'bestpics-species:%s'

MIN_VIEWING_REQUIREMENT = 3 # Must be rated three times to show up in scores

def random_species_with_multiple_photos():
    return Species.objects.get(slug = 'otter')
    while True:
        pk = r.srandmember(SPECIES_SET)
        if pk is None:
            update_redis_set()
            pk = r.srandmember(SPECIES_SET)
            if pk is None:
                raise ValueError('No species has more than 1 visible photo')
        try:
            return Species.objects.get(pk = pk)
        except Species.DoesNotExist:
            r.srem(SPECIES_SET, pk)

def random_photos_for_species(species, num=2):
    key = 'species-photo-ids:%s' % species.pk
    photo_ids = r.smembers(key)
    if not photo_ids or len(photo_ids) < 2:
        photo_ids = list(species.visible_photos().values_list('pk',flat=True))
        r.delete(key)
        for id in photo_ids:
            r.sadd(key, id)
            r.expire(key, 10 * 60)
    
    photos = list(
        Photo.objects.select_related('created_by').filter(
            pk__in = random.sample(photo_ids, num)
        )
    )
    random.shuffle(photos)
    return photos

def update_redis_set():
    r.delete(SPECIES_SET + '-temp')
    species_with_multiple_photos = Species.objects.filter(
        sightings__photos__is_visible = True
    ).annotate(                  
        num_photos = models.Count('sightings__photos')
    ).filter(num_photos__gt = 1)
    
    for species in species_with_multiple_photos:
        r.sadd(SPECIES_SET + '-temp', species.pk)
    
    r.rename(SPECIES_SET + '-temp', SPECIES_SET)

def generate_token():
    token = str(uuid.uuid1())
    r.set(token, 1)
    r.expire(token, 6 * 60)
    return token

def check_token(token):
    return r.get(token) is not None

def record_win(species, winner, loser):
    # We record the win-percentage for everything - what percentage of 
    # competitions it has been in has it won? We do this on a per-species 
    # basis to account for photos with multiple species that are great for 
    # one and bad for the other.
    winner_times_seen = r.incr(SEEN_KEY % winner)
    loser_times_seen = r.incr(SEEN_KEY % loser)
    winner_times_won = r.incr(WON_KEY % winner)
    loser_times_won = r.get(WON_KEY % loser) or 0
    
    winner_score = (
        float(winner_times_won) / float(winner_times_seen)
    )
    loser_score = (
        float(loser_times_won) / float(loser_times_seen)
    )
    
    # Update scores in the ordered - but ONLY for photos meeting minimum
    # viewing requirements
    if winner_times_seen >= MIN_VIEWING_REQUIREMENT:
        r.zadd(BESTPICS_KEY % species, winner, winner_score)
    
    if loser_times_seen >= MIN_VIEWING_REQUIREMENT:
        r.zadd(BESTPICS_KEY % species, loser, loser_score)
    
    return {
        'winner_times_seen': winner_times_seen,
        'winner_times_won': winner_times_won,
        'winner_score': winner_score * 100,
        'loser_times_seen': loser_times_seen,
        'loser_times_won': loser_times_won,
        'loser_score': loser_score * 100,
    }

def record_contribution_from(username):
    r.zincr('bestpic-contributors', username, 1)
    date = datetime.date.today().strftime('%Y-%m-%d')
    r.zincr('bestpic-contributors:%s' % date, username, 1)

def top_10_for_species(species):
    species_key = BESTPICS_KEY % species.pk
    pks = r.zrange(species_key, 0, 10, desc=True)
    metrics = [
        (r.zscore(species_key, pk) or 0, r.get(SEEN_KEY % pk) or 0, pk)
        for pk in pks
    ]
    # We award win percentage above all - if that's a tie, the one which has 
    # been in the most matches wins. If that's a tie, the one with the highest
    # pk (i.e. the one that was most recently added) wins, to keep the photos 
    # on the site 'fresh'.
    metrics.sort(reverse = True)
    photos = Photo.objects.in_bulk(pks)
    results = []
    for score, matches, pk in metrics:
        photo = photos[pk]
        photo.bestpic_score = score * 100
        photo.bestpic_matches = matches
        results.append(photo)
    return results

def species_has_top_10(species):
    species_key = BESTPICS_KEY % species.pk
    return r.zcard(species_key)
