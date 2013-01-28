from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime

class VotablePost(models.Model):
    """ super-model for all votable models """
    # meta-data
    creator = models.ForeignKey(User, related_name="created_proposals")
    create_date = models.DateTimeField(auto_now=True)

    @property
    def num_upvotes(self):
        return self.up_down_votes.filter(is_up=True).count()

    @property
    def num_downvotes(self):
        return self.up_down_votes.filter(is_up=False).count()

    @property
    def votescore(self):
        return self.num_updownvotes - self.num_downvotes

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
    # essentials
    proposal = models.ForeignKey(Proposal)
    motivation = models.TextField()

    def __unicode__(self):
        return "Comment on {}".format(self.proposal)
