'''
Created on Mar 2, 2013

@author: jonas
'''

from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from proposing.models import Proposal
import datetime

class Command(NoArgsCommand):
    help = 'Check all proposals and move the proposals which fit the conditions to the next round'

    def handle_noargs(self, *args, **kwargs):
        voting = 0
        finished = 0
        
        for proposal in Proposal.objects.filter(isFinished = False):
            
            if proposal.shouldStartVoting:
                proposal.isVoting = True
                proposal.voting_date = datetime.datetime.now()
                voting +=1
            # proposal might already be finished
            if proposal.shouldBeFinished:
                proposal.isFinished = True
                finished +=1
            proposal.save()
        
        self.stdout.write('Successfully updated:\n\t%d proposals to the voting phase\n\t%d proposals to the finished phase' % (voting, finished))