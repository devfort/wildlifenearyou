from django.core.management.base import BaseCommand, CommandError
from zoo.flickr.client import Flickr
from zoo.photos.models import Photo
from dateutil import parser
import time

class Command(BaseCommand):
    help = """
    Back-fill all previously imported Flickr photos with their date_taken
    """.strip()
    
    requires_model_validation = True
    can_import_settings = True
    
    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        client = Flickr()
        
        photos = Photo.objects.filter(
            taken_at__isnull = True
        ).exclude(flickr_id = '')
        
        for photo in photos:
            try:
                taken_at = parser.parse(
                    client.photos_getInfo(
                        photo_id = photo.flickr_id,
                        secret = photo.flickr_secret
                    )['photo']['dates']['taken']
                )
            except KeyError:
                print "No date found for id: %s" % photo.flickr_id
            else:
                photo.taken_at = taken_at
                photo.save()
                print "Saved date for %s" % photo.flickr_id
            time.sleep(2)
