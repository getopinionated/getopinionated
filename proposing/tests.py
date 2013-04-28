import datetime

from django.utils import timezone
from django.test import TestCase

from proposing.models import Proposal,Proxy,ProposalVote, Tag, ProposalType
from django.core.urlresolvers import reverse
from accounts.models import CustomUser
from django.contrib.auth.models import User
from document.models import Diff, FullDocument

class VoteCountTestCase(TestCase):
    def setUp(self):
        numusers = 10
        self.users = []
        for i in xrange(numusers):
            u = CustomUser(username="U%d"%i)
            u.save()
            self.users.append(u)
        
        numtags = 10
        self.tags = []
        for i in xrange(numtags):
            t = Tag(name="T%d"%i)
            t.save()
            self.tags.append(t)
        
        tupples = [(0,[],[1,2,3,4],True),
                   (0,[0],[1,2,3,4],False),
                   (1,[0,1],[2],False),
                   (2,[],[3,4],True),
                   ]
        self.proxies = []
        for tupple in tupples:
            p = Proxy(delegating = self.users[tupple[0]],isdefault=tupple[3])
            p.save()
            for t in tupple[1]:
                p.tags.add(self.tags[t])
            for d in tupple[2]:
                p.delegates.add(self.users[d])
            p.save()
            self.proxies.append(p)
        
        t = ProposalType()
        t.save()
        doc = FullDocument()
        doc.save()
        diff = Diff(fulldocument=doc)
        diff.save()
        self.proposal = Proposal(title="Test", diff=diff, proposal_type=t)
        self.proposal.save()
    
    def setupVotes(self,tupples):
        self.votes = []
        for tupple in tupples:
            p = ProposalVote(user=self.users[tupple[0]],proposal=self.proposal,value=tupple[1])
            p.save()
    
    def testVote1(self):
        self.setupVotes([(0,0)])
        self.assertEqual(self.proposal.avgProposalvoteScore, 0.0)
    
    def testVote2(self):
        self.setupVotes([(0,1)])
        self.assertEqual(self.proposal.avgProposalvoteScore, 1.0)
    
    def testVote3(self):
        self.setupVotes([(0,1),(1,0)])
        self.assertEqual(self.proposal.avgProposalvoteScore, 0.5)
        
    def testVote4(self):
        self.setupVotes([(0,-1),(1,1)])
        self.assertEqual(self.proposal.avgProposalvoteScore, 0.0)
    
    def testVote5(self):
        self.setupVotes([])
        self.assertEqual(self.proposal.avgProposalvoteScore, 0.0)
    
    def testVote6(self):
        self.setupVotes([(0,1),(0,1)]) #TODO: should protest! Illegal votes have been cast
        self.assertEqual(self.proposal.avgProposalvoteScore, 1.0)       

    def testVote7(self):
        self.setupVotes([(0,0),(3,3)])
        self.proposal.tags.add(self.tags[1])
        self.assertEqual(self.proposal.avgProposalvoteScore, 2.0)       

'''
class ProposalViewTests(TestCase):
    def test_index_view_with_no_polls(self):
        """
        If no polls exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('proposal:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No proposals are available.")
        self.assertQuerysetEqual(response.context['latest_proposal_list'], [])

    def test_index_view_with_a_past_poll(self):
        """
        Polls with a pub_date in the past should be displayed on the index page.
        """
        create_proposal(title="Past proposal.", extra_days=-30)
        response = self.client.get(reverse('proposal:index'))
        self.assertQuerysetEqual(
            response.context['latest_proposal_list'],
            ['<Proposal: Past proposal.>']
        )

    def test_index_view_with_a_future_poll(self):
        """
        Polls with a pub_date in the future should not be displayed on the
        index page.
        """
        create_proposal(title="Future proposal.", extra_days=30)
        response = self.client.get(reverse('proposal:index'))
        self.assertContains(response, "No proposals are available.", status_code=200)
        self.assertQuerysetEqual(response.context['latest_proposal_list'], [])

    def test_index_view_with_future_poll_and_past_poll(self):
        """
        Even if both past and future polls exist, only past polls should be
        displayed.
        """
        create_proposal(title="Past proposal.", extra_days=-30)
        create_proposal(title="Future proposal.", extra_days=30)
        response = self.client.get(reverse('proposal:index'))
        self.assertQuerysetEqual(
            response.context['latest_proposal_list'],
            ['<Proposal: Past proposal.>']
        )

    def test_index_view_with_two_past_polls(self):
        """
        The polls index page may display multiple polls.
        """
        create_proposal(title="Past proposal 1.", extra_days=-30)
        create_proposal(title="Past proposal 2.", extra_days=-5)
        response = self.client.get(reverse('proposal:index'))
        self.assertQuerysetEqual(
            response.context['latest_proposal_list'],
             ['<Proposal: Past proposal 2.>', '<Proposal: Past proposal 1.>']
        )
        
'''