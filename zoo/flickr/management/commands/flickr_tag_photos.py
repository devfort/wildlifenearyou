from django.core.management.base import BaseCommand, CommandError

from zoo.flickr import metadata
import time

class Command(BaseCommand):
    help = """
    Update tags and locations on ALL Flickr photos that need tagging (where 
    their owners have said that we should do this). This makes a LOT of 
    Flickr API requests.
    """.strip()
    
    requires_model_validation = True
    can_import_settings = True
    
    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        photos = metadata.get_photos_needing_tagging()
        count = photos.count()
        counter = 1
        for photo in photos:
            metadata.update_flickr_tags_for_photo(photo)
            print "%s/%s\tTagged %s" % (
                counter, count, photo.get_absolute_url()
            )
            counter += 1
            time.sleep(0.5)
        
        photos = metadata.get_photos_needing_geotagging()
        count = photos.count()
        counter = 1
        for photo in metadata.get_photos_needing_geotagging():
            metadata.update_flickr_location_for_photo(photo)
            print "%s/%s\tGeotagged %s" % (
                counter, count, photo.get_absolute_url()
            )
            counter += 1
            time.sleep(0.5)
