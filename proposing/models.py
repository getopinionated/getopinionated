from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime

class VotablePost(models.Model):
    """ super-model for all votable models """
    creator = models.ForeignKey(User, related_name="created_proposals")
    create_date = models.DateTimeField(auto_now=True)

    @property
    def votescore(self):
        num_upvotes = self.up_down_votes.filter(is_up=True).count()
        num_downvotes = self.up_down_votes.filter(is_up=False).count()
        return num_upvotes - num_downvotes

    def vote_from_user(self, user):
        uservotes = self.up_down_votes.filter(user=user)
        if uservotes:
            return uservotes[0]
        return None

    def user_can_vote(self, user):
        if self.creator == user:
            return False
        return not self.vote_from_user(user) != None

    def user_has_voted(self, user):
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
    diff_textual = models.TextField()

    def __unicode__(self):
        return "Proposal: {}".format(self.title)
    
    @property
    def diff_with_context(self):
        return self.diff_textual

class Comment(VotablePost):
    proposal = models.ForeignKey(Proposal)
    motivation = models.TextField()

    def __unicode__(self):
        return "Comment on {}".format(self.proposal)
