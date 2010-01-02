from django.core.management.base import BaseCommand, CommandError
from zoo.animals.models import Species
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment

class Command(BaseCommand):
    help = """
    ./manage.py merge_species slug1 slug2
    
    Merge the species with slug1 (the duplicate item) in to the species with
    slug2 - all sightings, comments and favourites attached to slug1 will be 
    moved over to point at slug2 instead, and slug1 will then be deleted.
    """.strip()
    
    requires_model_validation = True
    can_import_settings = True
    
    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError, 'Usage: /manage.py merge_species slug1 slug2'
        duplicate_slug = args[0]
        species_slug = args[1]
        
        try:
            duplicate = Species.objects.get(slug = duplicate_slug)
        except Species.DoesNotExist:
            raise CommandError, '%s is not a valid species' % duplicate_slug
        try:
            species = Species.objects.get(slug = species_slug)
        except Species.DoesNotExist:
            raise CommandError, '%s is not a valid species' % species_slug
        
        print "Move everything attached to %s to %s and delete %s ?" % (
            duplicate.slug, species.slug, duplicate.slug
        )
        if not raw_input().strip().lower().startswith('y'):
            raise CommandError, "You didn't type yes!"
        
        merge_duplicate_into_species(duplicate, species)
        
        print "You should now run:"
        print "  ./manage.py reindex_known_species"
        print "or the search interface is likely to break."

def merge_duplicate_into_species(duplicate, species):
    "duplicate will have all attached stuff moved to species, then be deleted"
    # Shift sightings across
    for sighting in duplicate.sightings.all():
        sighting.species = species
        sighting.save()
    
    # Shift favourites across
    for favourite in duplicate.favourited.all():
        favourite.species = species
        favourite.save()
    
    # Shift any comments across
    species_content_type = ContentType.objects.get(
        app_label = 'animals',
        model = 'species'
    )
    for comment in Comment.objects.filter(
        content_type = species_content_type,
        object_pk = duplicate.pk
    ):
        comment.content_object = species
        comment.save()
    
    # placespeciessolelyforlinking_set only exists to allow us to assign 
    # django.contrib.comments to species-at-zoo pages. Hence we need to 
    # loop through all of these on duplicate, then for each one check if 
    # there are any comments on it, then if there ARE ensure that a 
    # corresponding placespeciessolelyforlinking record exists on the 
    # species/place record, then re-assign the comment to it.
    # Haven't implemented this yet, so it prints out warnings instead.
    psl_content_type = ContentType.objects.get(
        app_label = 'places',
        model = 'placespeciessolelyforlinking'
    )
    for psl in duplicate.placespeciessolelyforlinking_set.all():
        comments = Comment.objects.filter(
            content_type = psl_content_type,
            object_pk = psl.pk
        )
        if comments:
            print "You need to manually fix the following comments:"
            for comment in comments:
                print comment.pk, repr(comment)
    
    # duplicate.trip_set.all() is just a ManyToMany through Sighting, so no 
    # need to deal with it separately.
    
    duplicate.delete()
