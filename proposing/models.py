from django.db import models
from django.utils import timezone
import datetime
from document.models import Diff
from django.contrib.auth.models import User

class VotablePost(models.Model):
    """ super-model for all votable models """
    creator = models.ForeignKey(User, related_name="created_proposals", null=True)
    create_date = models.DateTimeField(auto_now=True)

    @property
    def votescore(self):
        num_upvotes = self.up_down_votes.filter(is_up=True).count()
        num_downvotes = self.up_down_votes.filter(is_up=False).count()
        return num_upvotes - num_downvotes

    def vote_from_user(self, user):
        if not user.is_authenticated():
            return None
        uservotes = self.up_down_votes.filter(user=user)
        if uservotes:
            return uservotes[0]
        return None

    def user_can_vote(self, user):
        if not user.is_authenticated():
            return False
        if self.creator == user:
            return False
        return self.vote_from_user(user) == None

    def user_has_voted(self, user):
        if not user.is_authenticated():
            return False
        vote = self.vote_from_user(user)
        if vote != None:
            return "up" if vote.is_up else "down"
        return None

    def can_press_upvote(self, user):
        return self.user_can_vote(user) or self.user_has_voted(user) == 'up'

    def can_press_downvote(self, user):
        return self.user_can_vote(user) or self.user_has_voted(user) == 'down'

class UpDownVote(models.Model):
    user = models.ForeignKey(User, related_name="up_down_votes")
    post = models.ForeignKey(VotablePost, related_name="up_down_votes")
    date = models.DateTimeField(auto_now=True)
    is_up = models.BooleanField("True if this is an upvote")

class Proposal(VotablePost):
    title = models.CharField(max_length=255)
    motivation = models.TextField()
    diff = models.ForeignKey(Diff)

    def __unicode__(self):
        return "Proposal: {}".format(self.title)
    
    @property
    def diff_with_context(self):
        return self.diff.getNDiff()

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
