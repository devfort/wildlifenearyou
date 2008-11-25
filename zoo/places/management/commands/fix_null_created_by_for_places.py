from django.core.management.base import BaseCommand, CommandError

from zoo.places.models import Place

class Command(BaseCommand):
    help = """
    Place.objects.filter(created_by__isnull=True).update(created_by = 1) etc
    """.strip()

    requires_model_validation = True
    can_import_settings = True

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")

        Place.objects.filter(created_by__isnull=True).update(created_by = 1)
        Place.objects.filter(modified_by__isnull=True).update(modified_by = 1)
