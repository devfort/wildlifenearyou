from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = """
    Import faces from the faces/import_these directory
    """.strip()

    requires_model_validation = True
    can_import_settings = True

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")

        from zoo.faces.importer import import_faceparts
        import_faceparts()
