from django.core.management.base import BaseCommand, CommandError
from search import searches

class Command(BaseCommand):
    help = """
    Re-indexes known locations (by using the magic importer)
    """.strip()

    requires_model_validation = True
    can_import_settings = True

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")

        from zoo.geonames.importer import import_into_xapian
        import_into_xapian()
