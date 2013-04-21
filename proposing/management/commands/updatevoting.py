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
        expired_cnt = 0
        
        for proposal in Proposal.objects.filter(
                    ~Q(voting_stage='APPROVED'),
                    ~Q(voting_stage='REJECTED'),
                    ~Q(voting_stage='EXPIRED'),
                ):
            if proposal.shouldStartVoting():
                proposal.voting_stage = 'VOTING'
                proposal.voting_date = timezone.now()
                voting_cnt +=1
                proposal.save()
            if proposal.shouldBeFinished():
                proposal.initiateVoteCount()
                proposal.voting_stage = 'APPROVED' if proposal.isAccepted() else 'REJECTED'
                finished_cnt +=1
                proposal.save()
            if proposal.shouldExpire():
                proposal.voting_stage = 'EXPIRED'
                expired_cnt +=1
                proposal.save()
        
        self.stdout.write('Successfully updated:\n')
        self.stdout.write('{} proposals to the voting phase\n'.format(voting_cnt))
        self.stdout.write('{} proposals to the finished phase\n'.format(finished_cnt))
        self.stdout.write('{} proposals expired\n'.format(expired_cnt))