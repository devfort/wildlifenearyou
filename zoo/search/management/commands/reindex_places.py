from django.core.management.base import BaseCommand, CommandError
from search import searches

class Command(BaseCommand):
    help = """
    Re-indexes places (by calling .save() on all of them)
    """.strip()

    requires_model_validation = True
    can_import_settings = True

    def handle(self, *args, **options):
        searches.delete_places()

        from zoo.places.models import Place
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        import zoo.middleware
        for place in Place.objects.all():
            place.save()
