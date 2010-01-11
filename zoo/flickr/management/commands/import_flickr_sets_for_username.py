from zoo.flickr.client import Flickr
from zoo.flickr.models import FlickrSet
import time

def import_photo_sets_for_photos_belonging_to_user(user):
    f = Flickr()
    for photo in user.photos.all():
        if not photo.flickr_id:
            continue
        result = f.photos_getAllContexts(photo_id = photo.flickr_id)
        if 'set' not in result:
            continue
        sets = result['set']
        for set in sets:
            s, created = FlickrSet.objects.get_or_create(
                flickr_id = set['id'],
                defaults = {
                    'user': user,
                    'title': set['title'],
                }
            )
            s.photos.add(photo)
            print u"Added %s to set %s" % (photo, set)
        time.sleep(5)

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = """
    ./manage.py import_flickr_sets_for_username natbat
    
    Ensure all photos belonging to that user have had their Flickr sets 
    imported.
    """.strip()
    
    requires_model_validation = True
    can_import_settings = True
    
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError, 'Usage: /manage.py' \
                ' import_flickr_sets_for_username <username>'
        try:
            user = User.objects.get(username = args[0])
        except User.DoesNotExist:
            raise CommandError, '%s is not a valid username' % username
        
        import_photo_sets_for_photos_belonging_to_user(user)
