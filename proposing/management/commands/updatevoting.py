from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from django.db.models import Q
from django.utils import timezone
from proposing.models import Proposal, ProxyProposalVote, Proxy, Tag
import datetime

def concurrent():
    import sys
    import time
    import fcntl
    file_path = './manage.py'
    file_handle = open(file_path, 'w')
    try:
        fcntl.lockf(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return False
    
    except IOError:
        return True

class Command(NoArgsCommand):
    help = 'Check all proposals and move the proposals which fit the conditions to the next round'

    def handle_noargs(self, *args, **kwargs):
        # don't run a concurrent script twice
        if concurrent():
            return        
        
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
                Command.doVoteCount(proposal)
                Command.executeProposal(proposal)
                proposal.voting_stage = 'APPROVED' if proposal.isApproved() else 'REJECTED'
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
        
    @staticmethod
    def executeProposal(proposal):
        if proposal.isApproved():
            ## apply this diff
            try:
                proposal.diff.fulldocument.getFinalVersion().applyDiff(proposal.diff)
            except Exception as e:
                print "Error applying diff to final version: ", e
                # TODO: catch this in nice way
            ## convert other proposal diffs
            for proposal in Proposal.objects.filter(
                    ~Q(voting_stage='APPROVED'),
                    ~Q(voting_stage='REJECTED'),
                    ~Q(voting_stage='EXPIRED'),
                    ~Q(pk=proposal.pk),
                ):
                try:
                    proposal.diff.applyDiffOnThisDiff(proposal.diff)
                except Exception as e:
                    print "Error applying diff to other diffs: ", e
                    # TODO: catch this in nice way
        else:
            return

    @staticmethod
    def doVoteCount(proposal):
        
        # deleta all previous results (safety, this method may be called twice, even though it shouldn't)
        ProxyProposalVote.objects.filter(proposal=proposal).delete()
        
        # set up graph, doing as few queries as possible
        voters = proposal.proposal_votes.values('user')
        #exclude proxies from people who voted themselves
        proxies = Proxy.objects.exclude(delegating__in = voters).all()      
        #select edges with the correct tag
        validproxies = proxies.exclude(tags__in = Tag.objects.exclude(pk__in=proposal.tags.values('pk'))).filter(isdefault=False)
        #select default edges from delegating people not in the previous set
        validproxies = validproxies | (proxies.filter(isdefault=True).exclude(delegating__in = validproxies.values('delegating')))
        
        validproxies = list(validproxies)
        votes = list(proposal.proposal_votes.all())
        
        #TODO: check for users having made 2 votes, this seriously breaks the algorithm, other than not
        #      being democratic at all
        
        
        proxiecount = {} #to keep track in how many votes proxies result
        voterqueue = {}
        for vote in votes:
            mainvoter = vote.user
            voterqueue[vote] = [mainvoter]
            #following can be sped up. Sort lists before comparing elementwise
            i=0
            while i<len(voterqueue[vote]):
                voter = voterqueue[vote][i]
                i += 1
                if proxiecount.has_key(voter):
                    proxiecount[voter] += 1
                else:
                    proxiecount[voter] = 1
                for proxy in validproxies:
                    if (voter in proxy.delegates.all()) and (proxy.delegating not in voterqueue[vote]):
                        voterqueue[vote].append(proxy.delegating)
                        
        
        total = 0
        for vote in votes:
            numvotes = 0.0
            actualvote = ProxyProposalVote.objects.get_or_create(user=vote.user, proposal=proposal, value=vote.value, voted_self=True)[0]
            for voter in voterqueue[vote]:
                numvotes += 1.0 / float(proxiecount[voter])
                actualvote.vote_traject.add(voter)
                if voter!=vote.user:
                    proxyvote = ProxyProposalVote.objects.get_or_create(user=voter, proposal=proposal)[0]
                    proxyvote.vote_traject.add(vote.user)
                    proxyvote.value += float(vote.value) / float(proxiecount[voter])
                    proxyvote.numvotes = proxiecount[voter]
                    proxyvote.save()
            actualvote.numvotes = numvotes
            actualvote.save()
            total += numvotes * vote.value
        
        if total == 0.0:
            return 0
        average = total / len(proxiecount.keys())
        proposal.avgProposalvoteScore = average
