from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from django.db.models import Q
from django.utils import timezone
from proposing.models import Proposal
import datetime

class Command(NoArgsCommand):
    help = 'Check all proposals and move the proposals which fit the conditions to the next round'

    def handle_noargs(self, *args, **kwargs):
        voting_cnt = 0
        finished_cnt = 0
        
        for proposal in Proposal.objects.filter(~Q(voting_stage='FINISHED')):
            if proposal.shouldStartVoting():
                proposal.voting_stage = 'VOTING'
                proposal.voting_date = timezone.now()
                voting_cnt +=1
            # proposal might already be finished
            if proposal.shouldBeFinished():
                proposal.voting_stage = 'FINISHED'
                finished_cnt +=1
            proposal.save()
        
        self.stdout.write('Successfully updated:\n\t%d proposals to the voting phase\n\t%d proposals to the finished phase\n' % (voting_cnt, finished_cnt))