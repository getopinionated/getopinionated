## python imports
import traceback
import numpy
import itertools
import logging
## django imports
from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import datetime, timedelta
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from django.conf import settings
## project imports
from common.socialnetwork import posttotwitter
from accounts.models import CustomUser
from proposing.models import Proposal, ProxyProposalVote, Proxy, Tag, FinalProposalVote, AmendmentProposal, PositionProposal
from event.models import ProposalLifeCycleEvent

logger = logging.getLogger(__name__)

## try importing scipy for sparse matrix functionality
try:
    from scipy.sparse import identity as sparse_identity_matrix #(ignore 'no module named ...') pylint: disable=E0611
    from scipy.sparse.linalg import inv as invert_sparse_matrix #(ignore 'no module named ...') pylint: disable=E0611
except ImportError as scipy_importerror:
    logger.warning("Could not load scipy. Without scipy, I won't be able to calculate the result of the voting. Please install scipy > 0.12.0")
    def sparse_identity_matrix(length, **kwargs):
        raise scipy_importerror

def concurrent():
    import sys
    import time
    import fcntl
    file_path = './lock'
    file_handle =open(file_path, 'w') # --> empties this file apparently on MacOS
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
        constraints_cnt = 0
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
                voting_cnt += 1
                proposal.mail_sent = False
                posttotwitter("VOTING BOOTS ARE OPEN: " + proposal.title + " " + settings.DOMAIN_NAME +
                    reverse('proposals-detail', kwargs={'proposal_slug':proposal.slug}))
                proposal.save()

                ## add event
                ProposalLifeCycleEvent.new_event_and_create_listeners_and_email_queue_entries(
                    proposal=proposal,
                    new_voting_stage=proposal.voting_stage,
                )

            elif proposal.voting_stage == 'DISCUSSION' and proposal.minimalContraintsAreMet() and not proposal.voting_date:
                proposal.voting_date = proposal.estimatedVotingDate
                constraints_cnt += 1
                proposal.mail_sent = False
                proposal.save()

            elif proposal.shouldBeFinished():
                Command.doVoteCount(proposal)
                if proposal.isApproved():
                    proposal.execute()
                proposal.expire_date = timezone.now()
                proposal.voting_stage = 'APPROVED' if proposal.isApproved() else 'REJECTED'
                finished_cnt += 1
                if proposal.voting_stage == 'APPROVED':
                    posttotwitter("\"" + proposal.title + "\" made it in the program! " + settings.DOMAIN_NAME
                        + reverse('proposals-detail',kwargs={'proposal_slug':proposal.slug}))
                else:
                    posttotwitter("\"" + proposal.title + "\" was rejected! " + settings.DOMAIN_NAME
                        + reverse('proposals-detail',kwargs={'proposal_slug':proposal.slug}))
                proposal.mail_sent = False
                proposal.save()

                ## add event
                ProposalLifeCycleEvent.new_event_and_create_listeners_and_email_queue_entries(
                    proposal=proposal,
                    new_voting_stage=proposal.voting_stage,
                )

            elif proposal.shouldExpire():
                proposal.expire_date = timezone.now()
                proposal.voting_stage = 'EXPIRED'
                expired_cnt += 1
                proposal.mail_sent = False
                proposal.save()
                
                ## add event
                ProposalLifeCycleEvent.new_event_and_create_listeners_and_email_queue_entries(
                    proposal=proposal,
                    new_voting_stage=proposal.voting_stage,
                )
        
        self.stdout.write('Successfully updated:\n')
        self.stdout.write('{} proposals to the voting phase\n'.format(voting_cnt))
        self.stdout.write('{} proposals have met minimal constraints\n'.format(constraints_cnt))
        self.stdout.write('{} proposals to the finished phase\n'.format(finished_cnt))
        self.stdout.write('{} proposals expired\n'.format(expired_cnt))
        
    @staticmethod
    def doVoteCount(proposal):
        
        # these users have become inactive. Remove them from the voting results
        inactive_users = CustomUser.objects.filter(last_activity__lt=timezone.now()-timedelta(days=settings.DAYS_TO_INACTIVE))
        
        # delete all previous results (safety, this method may be called twice, even though it shouldn't)
        ProxyProposalVote.objects.filter(proposal=proposal).delete()
        FinalProposalVote.objects.filter(proposal=proposal).delete()
        # set up graph, doing as few queries as possible
        voters = proposal.proposal_votes.values('user')
        #exclude proxies from people who voted themselves
        proxies = Proxy.objects.exclude(delegating__in = voters).all()
        proxies = proxies.exclude(delegating__in = inactive_users)
        #select edges with the correct tag
        validproxies = proxies.filter(tags__in = proposal.tags.all()).filter(isdefault=False)
        #select default edges from delegating people not in the previous set
        validproxies = validproxies | (proxies.filter(isdefault=True).exclude(delegating__in = validproxies.values('delegating')))
        #logged_in_users = CustomUser.objects.all().exclude()
        # TODO@Jonas: Work in progress on filtering old users
        #validproxies = validproxies.exclude(delegating__in)
        validproxies = list(validproxies)
        votes = list(proposal.proposal_votes.all())
        voters = list(CustomUser.objects.filter(id__in=voters).all())
        
        
        
        if len(votes)==0:
            #no votes have been cast, no counting to do
            return
        #TODO: check for users having made 2 votes, this seriously breaks the algorithm, other than not
        #      being democratic at all
        
        '''first, set up a list of all relevant users of which the vote will actually count'''
        # backpropagation from the users who actually voted
        users = list(voters) #copy this list
        
        usertoidmap = {}
        for i, u in enumerate(users):
            usertoidmap[u.pk] = i
        
        edges = set([])
        
        fromcount = [0]*len(users)
        i = 0
        while i < len(users):
            current = users[i]
            for proxy in validproxies:
                if current in proxy.delegates.all():
                    delegating = proxy.delegating
                    if delegating not in users:
                        usertoidmap[delegating.pk] = len(users)
                        users.append(delegating)
                        fromcount.append(0)
                    f = usertoidmap[delegating.pk]
                    #print f,"->",i
                    if f != i: #no self-referring edges
                        edge = (f, i) # edge from a to b
                        edges.add(edge)
                        fromcount[f] += 1
            i += 1
        
        #print "In this test, there are",len(users),"users voting"
        '''next, convert this graph to a (sparse) system'''
        # This is where the magic happens. I will write down some day why this actually works.
        # In short, of a square matrix A, the following is true:
        # inv(I-A) = I + A + A^2 + A^3 + A^4 + ... if the right hand side converges
        
        system = sparse_identity_matrix(len(users), format='lil')#build matrix in lil format
        for edge in edges:
            system[edge[1], edge[0]] = -1.0/fromcount[edge[0]] #startnode splits his vote in equal parts
        
        system = system.tocsc()#convert to csc for the inverse
        #print "=========before========="
        #print system.todense()
        '''solve this sparse system'''
        if len(users)>1:
            system = invert_sparse_matrix(system)
        #print "=========after========="
        #print system.todense()
        '''Now count all the votes and store the data in the respective models'''
        
        mapidvotes = {}
        for v in votes:
            mapidvotes[usertoidmap[v.user.pk]] = v.value
        
        finalvotes = [0]*len(users)
        numvotes = [0]*len(users)
        cx = system.tocoo()    #convert to coo for efficient looping
        for touserid, fromuserid, vote in itertools.izip(cx.row, cx.col, cx.data):
            touserid, fromuserid = int(touserid), int(fromuserid)            
            if touserid in mapidvotes:
                finalvotes[fromuserid] += vote*mapidvotes[touserid]
            numvotes[touserid] += vote
            ppv = ProxyProposalVote(user_voting = users[touserid], user_proxied = users[fromuserid], proposal=proposal, numvotes=vote)
            ppv.save()
        
        totalresult = 0
        totalvotes = 0
        for pk, fv in enumerate(finalvotes):
            actual = (users[pk] in voters)
            fpv = FinalProposalVote(user = users[pk], proposal=proposal, numvotes=numvotes[pk], value=finalvotes[pk], voted_self=actual)
            fpv.save()
            #print users[pk].slug,"voted",finalvotes[pk],"with",numvotes[pk],"votes"
            if actual:
                #
                totalresult += numvotes[pk] * finalvotes[pk]
                totalvotes += numvotes[pk]
        
        proposal.avgProposalvoteScore = totalresult/totalvotes
        proposal.save()
        
        
