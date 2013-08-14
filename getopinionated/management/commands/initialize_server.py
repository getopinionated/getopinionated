from django.core.management.base import BaseCommand

class Command(BaseCommand):

    help = "Initializes the database for getopinionated for a first run"

    def handle(self, *args, **options):
        print 'cmd was called'
