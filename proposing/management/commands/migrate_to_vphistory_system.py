from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from proposing.models import VotablePostHistory, VotablePost
        
class Command(NoArgsCommand):
    help = "Migrates the database to the system where VotablePostHistory objects" + \
           " are kept for every change, including the first."

    def handle(self, *args, **options):
        """ Migrates the database to the system where VotablePostHistory objects are kept for
            every change.

        """
        for votablepost in VotablePost.objects.all():
            if not self.has_votablepost_history(votablepost):
                votablepost.build_history(editing_user=votablepost.creator) # creates a historical record clone and a VotablePostHistory
                print "created history for {}".format(repr(votablepost))

    @staticmethod
    def has_votablepost_history(votablepost):
        return votablepost.edit_history.count() > 0

