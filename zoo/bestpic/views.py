from zoo.shortcuts import render
from django.shortcuts import get_object_or_404
import utils
import time
from django_openid import signed
from zoo.photos.models import Photo
from zoo.animals.models import Species

def bestpic(request):
    species = utils.random_species_with_multiple_photos()
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
    
    photos = Photo.objects.in_bulk([winner, loser])
    
    context.update({
        'last_species': Species.objects.get(pk = species_pk),
        'last_winner': photos[winner],
        'last_loser': photos[loser]
    })
    return context

def bestpic_of_species(request, pk):
    species = get_object_or_404(Species, pk = pk)
    return render(request, 'bestpic/of_species.html', {
        'species': species,
        'top_10': utils.top_10_for_species(species),
    })
