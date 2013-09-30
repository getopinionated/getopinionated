from django.test import TestCase

from proposing.models import AmendmentProposal,Proxy,ProposalVote, Tag
from accounts.models import CustomUser
from document.models import Diff, FullDocument
from proposing.management.commands.updatevoting import Command

class VoteCountTestCase(TestCase):
    def setUp(self):
        numusers = 20
        self.users = []
        for i in xrange(numusers):
            u = CustomUser(username=u"U%d"%i)
            u.save()
            self.users.append(u)
        
        numtags = 10
        self.tags = []
        for i in xrange(numtags):
            t = Tag(name=u"T%d"%i)
            t.save()
            self.tags.append(t)
        
        tupples = [(0,[],[1,2,3,4],True),
                   (1,[],[2,3,4],True),
                   (2,[],[1,3,4],True),
                   (3,[],[5,6],True),
                   (4,[],[7,8],True),
                   (5,[],[9],True),
                   (7,[],[10],True),
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
        
        doc = FullDocument()
        doc.save()
        diff = Diff(fulldocument=doc)
        diff.save()
        self.proposal = AmendmentProposal(title="Test", diff=diff, motivation="Motivation")
        self.proposal.save()
    
    def setupVotes(self,tupples):
        self.votes = []
        for tupple in tupples:
            p = ProposalVote(user=self.users[tupple[0]],proposal=self.proposal,value=tupple[1])
            p.save()
    
    def testVote1(self):
        self.setupVotes([(0,0)])
        Command.doVoteCount(self.proposal)
        self.assertEqual(self.proposal.avgProposalvoteScore, 0.0)
    
    def testVote2(self):
        self.setupVotes([(0,1)])
        Command.doVoteCount(self.proposal)
        self.assertEqual(self.proposal.avgProposalvoteScore, 1.0)
    
    def testVote3(self):
        self.setupVotes([(10,1),(9,0)])
        Command.doVoteCount(self.proposal)
        self.assertEqual(self.proposal.avgProposalvoteScore, 0.5)
        
    def testVote4(self):
        self.setupVotes([(0,-1),(1,1)])
        Command.doVoteCount(self.proposal)
        self.assertEqual(self.proposal.avgProposalvoteScore, 1.0/3.0)
    
    def testVote5(self):
        self.setupVotes([])
        Command.doVoteCount(self.proposal)
        self.assertEqual(self.proposal.avgProposalvoteScore, 0.0)
    
    def testVote6(self):
        self.setupVotes([(0,1),(0,1)]) #TODO: should protest! Illegal votes have been cast
        Command.doVoteCount(self.proposal)
        self.assertEqual(self.proposal.avgProposalvoteScore, 1.0)       

    def testVote7(self):
        self.setupVotes([(0,0),(3,4)])
        self.proposal.tags.add(self.tags[1])
        Command.doVoteCount(self.proposal)
        self.assertEqual(self.proposal.avgProposalvoteScore, 3.0)       

