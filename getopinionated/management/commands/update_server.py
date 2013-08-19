from django.core.management.base import BaseCommand

class Command(BaseCommand):

    help = "Updates the database to the model required for the current version of getopinionated. You would run this after upgrading the getopinionated version."

    def handle(self, *args, **options):
        print 'cmd was called'
