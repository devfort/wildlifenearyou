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
