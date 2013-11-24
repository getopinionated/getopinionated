from copy import copy
from django.test import TestCase

from proposing.models import AmendmentProposal,Proxy,ProposalVote, Tag, VotablePostHistory
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

class ProposalTestCase(TestCase):
    document = None
    proposal1 = None
    proposal2 = None

    def _lines_to_document_content(self, lines):
        return'<br />'.join(lines)

    def setUp(self):
        # set up document
        document_content_raw = """
            Line 1
            Line 2
            Line 3
            Line 4
            Line 5
            Line 6
            Line 7
            Line 8
            Line 9
            Line 10
            Line 11
            Line 12
            Line 13
        """
        document_content_lines = [l.strip() for l in document_content_raw.split('\n') if l.strip()]
        document_content = self._lines_to_document_content(document_content_lines)
        self.document = FullDocument(
            title = "Test-document",
            content = document_content,
        )
        self.document.save()

        # set up proposal 1
        new_document_content_lines = copy(document_content_lines)
        new_document_content_lines[8] = 'ABCD'
        diff1 = Diff.generateDiff(document_content, self._lines_to_document_content(new_document_content_lines))
        diff1.fulldocument = self.document
        diff1.save()
        self.proposal1 = AmendmentProposal(
            title = 'testtitle',
            motivation = 'Test-motivation',
            diff = diff1,
            creator = None,
        )
        self.proposal1.save()
        self.proposal1.build_history(editing_user=None)

        # set up proposal 2
        new_document_content_lines = copy(document_content_lines)
        new_document_content_lines.pop(11)
        new_document_content_lines[1] = "DEFG"
        diff2 = Diff.generateDiff(document_content, self._lines_to_document_content(new_document_content_lines))
        diff2.fulldocument = self.document
        diff2.save()
        self.proposal2 = AmendmentProposal(
            title = 'TESTTITLE',
            motivation = 'Test-motivation for proposal 2',
            diff = diff2,
            creator = None,
        )
        self.proposal2.save()
        self.proposal2.build_history(editing_user=None)

    def testProposalSlug(self):
        """ Test Proposal's AutoSlugField """
        self.assertEqual(self.proposal1.slug, 'testtitle')
        self.assertEqual(self.proposal2.slug, 'testtitle-2')

    def testAmendmentExecute(self):
        """ Test AmendmentProposal.execute() """
        ## perform execute
        self.proposal1.execute()

        ## run tests
        self.assertEqual(AmendmentProposal.objects.count(), 2)
        self.assertEqual(AmendmentProposal.all_objects.count(), 5)
        self.assertEqual(VotablePostHistory.objects.count(), 3)
        # TODO: other tests

