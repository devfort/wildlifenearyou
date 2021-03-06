from django.core.management.base import BaseCommand, CommandError
from search import searches

class Command(BaseCommand):
    help = """
    Re-indexes users (by calling .save() on all of them)
    """.strip()

    requires_model_validation = True
    can_import_settings = True

    def handle(self, *args, **options):
        # Delete any old database first
        searches.delete_users()
        from zoo.accounts.models import Profile
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        import zoo.common.middleware # To turn on the Searchify magic
        for user in Profile.objects.all():
            user.save()
            print "Re-indexed %s" % user
