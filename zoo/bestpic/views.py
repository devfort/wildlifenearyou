from zoo.shortcuts import render
from django.shortcuts import get_object_or_404
import utils
import time, datetime
from django_openid import signed
from zoo.photos.models import Photo
from zoo.animals.models import Species
from redis_db import r

# Track this number of species so logged in users don't see repeats
SEEN_SPECIES_COUNT = 150

def bestpic(request):
    if request.user.is_anonymous():
        species = utils.random_species_with_multiple_photos()
    else:
        species = utils.random_species_with_multiple_photos(request.user)
    photo1, photo2 = utils.random_photos_for_species(species, 2)
    # We use a token to ensure any given form we serve up can only be
    # submitted once. Used tokens are stored in Redis for 6 minutes. Forms
    # are time-stamped, and a submission from a form older than five minutes
    # (or one with a token within the 6 minute cache) will silently be 
    # discarded.
    token = utils.generate_token()
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
    try:
        options = signed.loads(request.POST.get('options', ''))
    except ValueError:
        return {}
    if (int(time.time()) - options['time']) > (5 * 60):
        return {} # Form is too old
    if not utils.check_token(options['token']):
        return {} # Token invalid
    
    species_pk = options['species']
    contestants = options['contestants']
    
    winner = int(request.POST.get('winner', ''))
    if not winner:
        return {}
    
    loser = (set(contestants) - set([winner])).pop()
    
    # Record a win!
    context = utils.record_win(species_pk, winner, loser)
    if not request.user.is_anonymous():
        utils.record_contribution_from(request.user.username)
    
    photos = Photo.objects.select_related(
        'created_by'
    ).in_bulk([winner, loser])
    
    last_species = Species.objects.get(pk = species_pk)
    
    description = '''
        %s: <a href="%s">%s</a>: <a href="%s"><img src="%s"></a> beat 
        <a href="%s"><img src="%s"></a>
        ''' % (
            str(datetime.datetime.now()),
            last_species.get_absolute_url(),
            last_species.common_name,
            photos[winner].get_absolute_url(),
            photos[winner].thumb_75_url(),
            photos[loser].get_absolute_url(),
            photos[loser].thumb_75_url(),
        )
    if not request.user.is_anonymous():
        description += ' (rated by <a href="%s">%s</a>)' % (
            request.user.username, request.user.username
        )
        # And record the species so we don't show it to them multiple times
        set_key = utils.USER_SEEN_SET % request.user.username
        list_key = utils.USER_SEEN_LIST % request.user.username
        r.push(list_key, species_pk, head=True)
        r.sadd(set_key, species_pk)
        if r.scard(set_key) >= SEEN_SPECIES_COUNT:
            r.srem(set_key, r.pop(list_key, tail=True))
    
    r.push('bestpic-activity', description, head=True)
    r.ltrim('bestpic-activity', 0, 200)
    
    context.update({
        'last_species': last_species,
        'last_winner': photos[winner],
        'last_loser': photos[loser],
        'show_link_to_best': utils.species_has_top_10(last_species),
    })
    return context

def activity(request):
    "Shows recent activity on this feature"
    return render(request, 'bestpic/activity.html', {
        'activity': r.lrange('bestpic-activity', 0, 200),
    })

def bestpic_of_species(request, slug):
    species = get_object_or_404(Species, slug = slug)
    return render(request, 'bestpic/of_species.html', {
        'species': species,
        'top_10': utils.top_10_for_species(species),
    })
