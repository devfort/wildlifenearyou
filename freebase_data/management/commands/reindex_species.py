from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = """
    Import species from freebase dump in to your personal Xapian index.
    """.strip()

    requires_model_validation = True
    can_import_settings = True

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")

        from zoo.freebase.importer import import_into_xapian
        import_into_xapian()
