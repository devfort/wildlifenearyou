from zoo.bestpic.utils import update_redis_set
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = """
    Update the redis sets used by the /best/ voting tool
    """.strip()
    
    requires_model_validation = True
    can_import_settings = True
    
    def handle(self, *args, **options):
        update_redis_set()
