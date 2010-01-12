from django.contrib.auth.models import User
from faces import generate

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = """
    Regenerate static face files for every user.
    """.strip()

    requires_model_validation = True
    can_import_settings = True

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        for user in User.objects.all():
            print user, generate.generate_faces_for_user(user)

