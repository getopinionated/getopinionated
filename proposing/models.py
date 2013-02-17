from django.db import models
from django.utils import timezone
import datetime
from document.models import Diff
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from common.stringify import niceBigInteger

class VotablePost(models.Model):
    """ super-model for all votable models """
    creator = models.ForeignKey(User, related_name="created_proposals", null=True)
    create_date = models.DateTimeField(auto_now_add=True)

    @property
    def numberofcomments(self):
        return self.up_down_votes.count()
    
    @property
    def upvotescore(self):
        num_upvotes = self.up_down_votes.filter(is_up=True).count()
        num_downvotes = self.up_down_votes.filter(is_up=False).count()
        return num_upvotes - num_downvotes

    def updownvote_from_user(self, user):
        if not user.is_authenticated():
            return None
        uservotes = self.up_down_votes.filter(user=user)
        if uservotes:
            return uservotes[0]
        return None

    def user_can_updownvote(self, user):
        if not user.is_authenticated():
            return False
        if self.creator == user:
            return False
        return self.updownvote_from_user(user) == None

    def user_has_updownvoted(self, user):
        if not user.is_authenticated():
            return False
        vote = self.updownvote_from_user(user)
        if vote != None:
            return "up" if vote.is_up else "down"
        return None

    def can_press_upvote(self, user):
        return self.user_can_updownvote(user) or self.user_has_updownvoted(user) == 'up'

    def can_press_downvote(self, user):
        return self.user_can_updownvote(user) or self.user_has_updownvoted(user) == 'down'

class UpDownVote(models.Model):
    user = models.ForeignKey(User, related_name="up_down_votes")
    post = models.ForeignKey(VotablePost, related_name="up_down_votes")
    date = models.DateTimeField(auto_now=True)
    is_up = models.BooleanField("True if this is an upvote")

class ProposalVote(models.Model):
    user = models.ForeignKey(User, related_name="proposal_votes")
    proposal = models.ForeignKey(VotablePost, related_name="proposal_votes")
    date = models.DateTimeField(auto_now=True)
    value = models.IntegerField("The value of the vote")

class Proposal(VotablePost):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    motivation = models.TextField()
    diff = models.ForeignKey(Diff)
    views = models.IntegerField(default=0)
    merged = models.BooleanField(default=False)

    def __unicode__(self):
        return "Proposal: {}".format(self.title)
    
    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.slug = slugify(self.title)
        super(Proposal, self).save(*args, **kwargs)

    @property
    def diff_with_context(self):
        return self.diff.getNDiff()

    @property
    def proposalvotescore(self):
        total = 0
        for i in xrange(-5,6):
            num_votes = self.proposal_votes.filter(value = i).count()
            total += i*num_votes
        return total

    @property
    def isVoting(self):
        return self.upvotescore>10
    
    @property
    def isFinished(self):
        return self.proposalvotescore>10

    def addView(self):
        self.views += 1
        self.save()
    
    def proposalvote_from_user(self, user):
        if not user.is_authenticated():
            return None
        uservotes = self.proposal_votes.filter(user=user)
        if uservotes:
            return uservotes[0]
        return None

    def user_has_proposalvoted(self, user):
        if not user.is_authenticated():
            return False
        vote = self.proposalvote_from_user(user)
        if vote != None:
            return vote.value
        return None

    def user_can_proposalvote(self, user):
        if not user.is_authenticated():
            return False
        # You can vote on your own proposals
        #if self.creator == user:
        #    return False
        return self.proposalvote_from_user(user) == None

    def proposalIsAccepted(self):
        return self.proposalvotescore>0

    def initiateVoteCount(self):
        if self.proposalIsAccepted():
            self.diff.fulldocument.getFinalVersion().applyDiff(self.diff)
            proposals = Proposal.objects.filter(merged=False,)
            for proposal in proposals:
                if proposal.pk == self.pk:
                    continue
                if proposal.merged == True:
                    continue
                proposal.diff.applyDiffOnThisDiff(self.diff)
            self.merged = True
            self.save()
        else:
            return
        
        
class Comment(VotablePost):
    # settings
    COMMENT_COLORS = (
        ('POS', 'positive'),
        ('NEUTR', 'neutral'),
        ('NEG', 'negative'),
    )
    # fields
    proposal = models.ForeignKey(Proposal)
    motivation = models.TextField()
    color = models.CharField(max_length=10, choices=COMMENT_COLORS, default='NEUTR')

    def __unicode__(self):
        return "Comment on {}".format(self.proposal)

class Tag(models.Model):
    proposal = models.ManyToManyField(Proposal, related_name="tags")
    title = models.CharField(max_length=35)