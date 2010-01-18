from zoo.shortcuts import render
from models import random_species_with_multiple_photos, record_win
import random, uuid, time
from django_openid import signed
import redis
from zoo.photos.models import Photo
from zoo.animals.models import Species

def bestpic(request):
    species = random_species_with_multiple_photos()
    photo1, photo2 = random.sample(species.visible_photos(), 2)
    # We use a token to ensure any given form we serve up can only be
    # submitted once. Used tokens are stored in Redis for 6 minutes. Forms
    # are time-stamped, and a submission from a form older than five minutes
    # (or one with a token within the 5 minute cache) will silently be 
    # discarded.
    token = str(uuid.uuid1())
    r = redis.Redis()
    r.set(token, 1)
    r.expire(token, 6 * 60)
    context = {
        'species': species,
        'photo1': photo1,
        'photo2': photo2,
        'options': signed.dumps({
            'species': species.pk,
            'contestants': [photo1.pk, photo2.pk],
            'token': token,
            'time': int(time.time()),
        }),
        'request_path': request.path,
    }
    
    if request.method == 'POST':
        context.update(process_submission(request))
    
    return render(request, 'bestpic/index.html', context)

def process_submission(request):
    # Process the previous submission
    r = redis.Redis()
    try:
        options = signed.loads(request.POST.get('options', ''))
    except ValueError:
        return {}
    if (int(time.time()) - options['time']) > (5 * 60):
        return {} # Form is too old
    if not r.get(options['token']):
        return {} # Token invalid
    
    species_pk = options['species']
    contestants = options['contestants']
    
    winner = int(request.POST.get('winner', ''))
    if not winner:
        return {}
    
    loser = (set(contestants) - set([winner])).pop()
    
    # Record a win!
    context = record_win(species_pk, winner, loser)
    print "Species %s: Win for %s v.s. %s" % (species_pk, winner, loser)
    
    photos = Photo.objects.in_bulk([winner, loser])
    
    context.update({
        'last_species': Species.objects.get(pk = species_pk),
        'last_winner': photos[winner],
        'last_loser': photos[loser]
    })
    return context
