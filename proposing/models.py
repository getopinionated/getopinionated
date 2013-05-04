from __future__ import division
import datetime
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.template.defaultfilters import slugify
from common.stringify import niceBigInteger
from document.models import Diff
from accounts.models import CustomUser
from django.db.models.aggregates import Sum


class VotablePost(models.Model):
    """ super-model for all votable models """
    creator = models.ForeignKey(CustomUser, related_name="created_proposals", null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)

    @property
    def upvote_score(self):
        num_upvotes = self.up_down_votes.filter(is_up=True).count()
        num_downvotes = self.up_down_votes.filter(is_up=False).count()
        return num_upvotes - num_downvotes

    def updownvoteFromUser(self, user):
        if not user.is_authenticated():
            return None
        uservotes = self.up_down_votes.filter(user=user)
        if uservotes:
            return uservotes[0]
        return None

    def userCanUpdownvote(self, user):
        if not user.is_authenticated():
            return False
        if self.creator == user:
            return False
        return self.updownvoteFromUser(user) == None

    def userHasUpdownvoted(self, user):
        if not user.is_authenticated():
            return False
        vote = self.updownvoteFromUser(user)
        if vote != None:
            return "up" if vote.is_up else "down"
        return None

    def canPressUpvote(self, user):
        return self.userCanUpdownvote(user) or self.userHasUpdownvoted(user) == 'up'

    def canPressDownvote(self, user):
        return self.userCanUpdownvote(user) or self.userHasUpdownvoted(user) == 'down'

class UpDownVote(models.Model):
    user = models.ForeignKey(CustomUser, related_name="up_down_votes")
    post = models.ForeignKey(VotablePost, related_name="up_down_votes")
    date = models.DateTimeField(auto_now=True)
    is_up = models.BooleanField("True if this is an upvote")

class Tag(models.Model):
    name = models.CharField(max_length=35)
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

class ProposalType(models.Model):
    name = models.CharField(max_length=255)
    daysUntilVotingStarts = models.IntegerField("Days until voting starts", default=7)
    minimalUpvotes = models.IntegerField("Minimal upvotes", default=3)
    daysUntilVotingFinishes = models.IntegerField("Days until voting finishes", default=7)
    daysUntilVotingExpires = models.IntegerField("Days until proposal expires", default=60, help_text="Starts from proposal creation date, expiration is due to lack of interest.")

    def __unicode__(self):
        return self.name

class Proposal(VotablePost):
    # settings
    QUORUM_SIZE = 1 # minimal # of proposalvotes for approvement
    VOTING_STAGE = (
        ('DISCUSSION', 'Discussion'),
        ('VOTING', 'Voting'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
    )
    # fields
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    motivation = models.TextField()
    diff = models.ForeignKey(Diff)
    views = models.IntegerField(default=0)
    voting_stage = models.CharField(max_length=20, choices=VOTING_STAGE, default='DISCUSSION')
    voting_date = models.DateTimeField(default=None, null=True, blank=True)
    proposal_type = models.ForeignKey(ProposalType)
    tags = models.ManyToManyField(Tag, related_name="proposals")

    def __unicode__(self):
        return self.title

    @property
    def totalvotescore(self):
        return self.upvote_score + self.proposal_votes.count()

    @property
    def number_of_comments(self):
        return self.comments.count()

    def finishedVoting(self):
        return self.voting_stage == 'APPROVED' or self.voting_stage == 'REJECTED'

    @property
    def estimatedVotingDate(self):
        properties = self.proposal_type
        if self.voting_stage == 'DISCUSSION':
            nominal_date = self.create_date + datetime.timedelta(days=properties.daysUntilVotingStarts)
            return nominal_date if timezone.now() < nominal_date else timezone.now()
        else:
            return self.voting_date

    @property
    def estimatedFinishDate(self):
        properties = self.proposal_type
        return self.estimatedVotingDate + datetime.timedelta(days=properties.daysUntilVotingFinishes)

    @property
    def expirationDate(self):
        """ date the proposal expires because lack of interest """
        properties = self.proposal_type
        if self.minimalContraintsAreMet():
            return None
        return self.create_date + datetime.timedelta(days=properties.daysUntilVotingExpires)

    def minimalContraintsAreMet(self):
        """ True if non-date constraints are met """
        properties = self.proposal_type
        return self.upvote_score > properties.minimalUpvotes

    def shouldStartVoting(self):
        # check relevance
        if self.voting_stage != 'DISCUSSION':
            return False
        # should start voting if start properties fullfilled
        properties = self.proposal_type
        shouldStartVoting = (timezone.now() > self.create_date + datetime.timedelta(days=properties.daysUntilVotingStarts)
                            and
                            self.minimalContraintsAreMet())
        return shouldStartVoting

    def shouldBeFinished(self):
        # check relevance
        if self.voting_stage != 'VOTING':
            return False
        # should finish voting if end properties fullfilled
        properties = self.proposal_type
        shouldBeFinished = timezone.now() > self.voting_date + datetime.timedelta(days=properties.daysUntilVotingFinishes)
        return shouldBeFinished

    def shouldExpire(self):
        return self.expirationDate and timezone.now() > self.expirationDate

    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.slug = slugify(self.title)
        super(Proposal, self).save(*args, **kwargs)

    def isValidTitle(self, title):
        """ Check if slug derived from title already exists,
            the title is then automatically also unique.
            Keeps into account possibility of already existing object.
        """
        titleslug = slugify(title)
        try:
            proposal = Proposal.objects.get(slug=titleslug)
            return self.id == proposal.id
        except Proposal.DoesNotExist:
            return True

    @property
    def diffWithContext(self):
        return self.diff.getNDiff()


###################################################################################################

    @property
    def avgProposalvoteScore(self):
        
        # deleta all previous results (safety, this method may be called twice, even though it shouldn't)
        ProxyProposalVote.objects.filter(proposal=self).delete()
        
        # set up graph, doing as few queries as possible
        voters = self.proposal_votes.values('user')
        #exclude proxies from people who voted themselves
        proxies = Proxy.objects.exclude(delegating__in = voters).all()      
        #select edges with the correct tag
        validproxies = proxies.exclude(tags__in = Tag.objects.exclude(pk__in=self.tags.values('pk'))).filter(isdefault=False)
        #select default edges from delegating people not in the previous set
        validproxies = validproxies | (proxies.filter(isdefault=True).exclude(delegating__in = validproxies.values('delegating')))
        
        validproxies = list(validproxies)
        votes = list(self.proposal_votes.all())
        
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
            actualvote = ProxyProposalVote.objects.get_or_create(user=vote.user, proposal=self, value=vote.value, voted_self=True)[0]
            for voter in voterqueue[vote]:
                numvotes += 1.0 / float(proxiecount[voter])
                actualvote.vote_traject.add(voter)
                if voter!=vote.user:
                    proxyvote = ProxyProposalVote.objects.get_or_create(user=voter, proposal=self)[0]
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
        return average

        
    def addView(self):
        self.views += 1
        self.save()

    def proposalvoteFromUser(self, user):
        if not user.is_authenticated():
            return None
        uservotes = self.proposal_votes.filter(user=user)
        if uservotes:
            return uservotes[0]
        return None

    def userHasProposalvoted(self, user):
        if not user.is_authenticated():
            return None
        vote = self.proposalvoteFromUser(user)
        if vote != None:
            return vote.value
        return None

    def userHasProposalvotedOn(self, user, option):
        return self.userHasProposalvoted(user) == int(option)

    def isApproved(self):
        # QUESTION: should quorum be number of voters of number of votes (c.f.r. liquid democracy, one person can have many votes)
        # Quorum is always number of voters, not number of votes. A quorum is needed to avoid under-the-radar-behaviour.
        return self.avgProposalvoteScore > 0 and self.proposal_votes.count() >= self.QUORUM_SIZE

    def initiateVoteCount(self):
        if self.isApproved():
            ## apply this diff
            try:
                self.diff.fulldocument.getFinalVersion().applyDiff(self.diff)
            except Exception as e:
                print "Error applying diff to final version: ", e
                # TODO: catch this in nice way
            ## convert other proposal diffs
            for proposal in Proposal.objects.filter(
                    ~Q(voting_stage='APPROVED'),
                    ~Q(voting_stage='REJECTED'),
                    ~Q(voting_stage='EXPIRED'),
                    ~Q(pk=self.pk),
                ):
                try:
                    proposal.diff.applyDiffOnThisDiff(self.diff)
                except Exception as e:
                    print "Error applying diff to other diffs: ", e
                    # TODO: catch this in nice way
        else:
            return

    def commentsAllowed(self):
        return self.voting_stage == 'DISCUSSION'

    @staticmethod
    def voteOptions():
        """ returns vote options, fit for use in template """
        return [
            ('-5', 'Against'),
            ('-4', ''),
            ('-3', ''),
            ('-2', ''),
            ('-1', ''),
            ('0', 'Neutral'),
            ('1', ''),
            ('2', ''),
            ('3', ''),
            ('4', ''),
            ('5', 'In favor'),
        ]

    def dateToPx(self, date):
        """ get pixels for timeline in detail.html """
        ## check sanity
        assert self.voting_stage != 'EXPIRED'
        ## get vars
        d10 = datetime.timedelta(days=10)
        begin, voting, finish = self.create_date.date(), self.estimatedVotingDate.date(), self.estimatedFinishDate.date()
        ## get fixed places
        fixed_dateToPx = [
            (begin - d10, -50),
            (begin, 0),
            (voting, 200),
            (finish, 400),
            (finish + d10, 450),
        ]
        ## linear interpolation between fixed dates
        px = fixed_dateToPx[0][1]
        for (date1, px1), (date2, px2) in zip(fixed_dateToPx[:-1], fixed_dateToPx[1:]):
            if date1 < date <= date2:
                px = px1 + (px2-px1)/(date2-date1).days*(date-date1).days
        return px if date < fixed_dateToPx[-1][0] else fixed_dateToPx[-1][1];

    def currentDateToPx(self):
        if self.voting_stage != 'EXPIRED':
            return self.dateToPx(timezone.now().date())
        else:
            return 300

    def expirationDateToPx(self):
        ## check if expiration date is relevant
        if not self.expirationDate:
            return None
        ## only show expiration if it is in the near future (30 days)
        if (self.expirationDate - timezone.now()).days > 30:
            return None
        ## calculate pixels
        return self.dateToPx(self.expirationDate.date())

    def numVotesOn(self, vote_value):
        a = self.total_proxy_proposal_votes.filter(value = vote_value, voted_self=True).aggregate(Sum('numvotes'))
        return a['numvotes__sum'] or 0
    
    def numVotesToPx(self, vote_value):
        max_num_votes = max([self.numVotesOn(i) for i in xrange(-5,6)])
        if max_num_votes==0:
            return 0
        num_votes = self.numVotesOn(int(vote_value))
        fraction = num_votes / max_num_votes
        BAR_HEIGHT = 150 # px
        return fraction * BAR_HEIGHT

    def votesOn(self, vote_value):
        return self.total_proxy_proposal_votes.filter(value = vote_value, voted_self=True)

class Comment(VotablePost):
    # settings
    COMMENT_COLORS = (
        ('POS', 'positive'),
        ('NEUTR', 'neutral'),
        ('NEG', 'negative'),
    )
    # fields
    proposal = models.ForeignKey(Proposal, related_name="comments")
    motivation = models.TextField()
    color = models.CharField(max_length=10, choices=COMMENT_COLORS, default='NEUTR')

    def __unicode__(self):
        return "Comment on {}".format(self.proposal)

class ProposalVote(models.Model):
    user = models.ForeignKey(CustomUser, related_name="proposal_votes")
    proposal = models.ForeignKey(Proposal, related_name="proposal_votes")
    date = models.DateTimeField(auto_now=True)
    value = models.IntegerField("The value of the vote")

class ProxyProposalVote(models.Model):
    user = models.ForeignKey(CustomUser, related_name="total_proxy_proposal_votes")
    proposal = models.ForeignKey(Proposal, related_name="total_proxy_proposal_votes")
    value = models.FloatField("The value of the vote", default=0.0)
    vote_traject = models.ManyToManyField(CustomUser)
    voted_self = models.BooleanField(default=False)
    numvotes = models.FloatField(default=0)

'''
    object containing the issued proxies for the voting system
'''
class Proxy(models.Model):
    delegating = models.ForeignKey(CustomUser, related_name="proxies")
    delegates = models.ManyToManyField(CustomUser, related_name="received_proxies")
    tags = models.ManyToManyField(Tag, related_name="allproxies")
    isdefault = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Proxies"
