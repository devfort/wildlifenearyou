import httplib2
from photos.models import Photo
from django.contrib.auth.models import User
from trips.models import Trip
from django.core.management.base import BaseCommand, CommandError
from flickr.client import Flickr
import time

THUMB_UNAVAILABLE = 'http://l.yimg.com/g/images/photo_unavailable_s.gif'

http = httplib2.Http()

class Command(BaseCommand):
    help = """
    ./manage.py fix_broken_photo_secrets user simon
    ./manage.py fix_broken_photo_secrets trip 456
    
    For each photo belonging to that user or trip, check that the thumbnail 
    URL still works - if it doesn't, the secret has probably changed so pull 
    in an updated secret from the Flickr API.
    """.strip()
    
    requires_model_validation = True
    can_import_settings = True
    
    def handle(self, *args, **options):
        if len(args) != 2 or args[0] not in ('trip', 'user'):
            raise CommandError, 'Usage: see help'
        
        if args[0] == 'user':
            obj = User.objects.get(username = args[1])
        elif args[0] == 'trip':
            obj = Trip.objects.get(pk = args[1])
        else:
            raise CommandError, 'Usage: see help'
        
        flickr_photos = obj.photos.exclude(flickr_id = None)
        print "%s photos associated with %s" % (
            flickr_photos.count(), obj
        )
        need_fixing = []
        i = 1
        for photo in flickr_photos:
            url = photo.thumb_75_url()
            response, content =  http.request(url)
            if 'content-location' in response and \
                response['content-location'] == THUMB_UNAVAILABLE:
                print "%d: Needs fixing: %s" % (i, photo.get_absolute_url())
                need_fixing.append(photo)
            else:
                print "%d: Photo is fine: %s" % (i, photo.get_absolute_url())
            time.sleep(1)
            i += 1
        
        flickr = Flickr()
        for photo in need_fixing:
            info = flickr.photos_getInfo(photo_id = photo.flickr_id)['photo']
            photo.flickr_secret = info['secret']
            photo.flickr_server = info['server']
            photo.save()
            print "Fixed %s" % photo.get_absolute_url()
            time.sleep(2)
