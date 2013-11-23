from __future__ import division
import datetime, logging, traceback
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.db.models.aggregates import Sum
from django.contrib.auth.models import Group, User
from django.conf import settings
from django.template.defaultfilters import truncatechars
from common.autoslug import AutoSlugField
from common.templatetags.filters import slugify
from common.models import DisableableModel
from document.models import Diff
from accounts.models import CustomUser

logger = logging.getLogger(__name__)

class VotablePost(DisableableModel):
    """ Base class for all upvotable posts.

    This means textual contributions from users that can be up- or downvoted by other Users.

    Note: There are two kinds of VotablePost:
             1) Enabled and formerly enabled objects:
                These objects can be treaded as normal objects. Enabled objects are mutable
                but they should be disabled instead of deleted.

             2) Historical records:
                These objects are always disabled, have the is_historical_record flag and are
                immutable. They are used to reconstruct the history of a VotablePost, together
                with the VotablePostHistory model.

          Every enabled object should have a kwasi-identical historical record copy. In other
          words, every major change should be accompanied with the creation of a historical
          record copy and a VotablePostHistory object.

    """
    creator = models.ForeignKey(CustomUser, related_name="created_proposals", null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    is_historical_record = models.BooleanField(default=False, help_text="If True, this object is a historical record. "
        "This can be used to distinguish historical records from 'removed' (i.e. disabled) objects.")

    @property
    def up_down_votes(self):
        return self.up_down_votes_including_disabled.filter(enabled=True)

    @property
    def upvote_score(self):
        v = self.up_down_votes.aggregate(Sum('value'))['value__sum']
        return v if v else 0 # v is None when no votes have been cast

    @property
    def popularity(self):
        """ A numerical measure for how popular a proposal is. This defines the position in lists.

        Note: this method can be overridden if better measures can be found.

        """
        return self.upvote_score

    @property
    def number_of_edits(self):
        return max(0, self.edit_history.count() - 1)

    def __unicode__(self):
        """ [override] Make sure a VotablePost object prints out the more specific to_string of its child. """
        return self.cast().to_string()

    def to_string(self):
        """ Make sure to override this in every child. """
        raise NotImplementedError("This method should be overridden by every child.")

    def can_change_field(self, field_name):
       """ [override] make all attributes mutable if this object is enabled. """
       # return True if enabled attribute does not yet exist (in re-building phase, we can allow more)
       if not hasattr(self, 'enabled'):
           return True

       # disable immutability check if enabled
       if self.enabled:
           return True

       # normal operation
       return super(VotablePost, self).can_change_field(field_name)

    def build_history(self, editing_user):
        """ Create two new model objects:
                1) A disabled copy of self with is_historical_record=True
                2) A VotablePostHistory
        
        """
        # create disabled copy
        historical_record = self.get_mutable_copy()
        historical_record.is_historical_record = True
        historical_record.save()
        historical_record.disable()

        # create VotablePostHistory
        vp_history = VotablePostHistory(
            editing_user=editing_user,
            post=self,
            post_at_date=historical_record,
        )
        vp_history.save()
        return (historical_record, vp_history)

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
            return "up" if vote.value==1 else "down"
        return None

    def hasUpvoted(self, user):
        return self.userHasUpdownvoted(user) == 'up'

    def hasDownvoted(self, user):
        return self.userHasUpdownvoted(user) == 'down'

    def canPressUpvote(self, user):
        return self.userCanUpdownvote(user) or self.userHasUpdownvoted(user) == 'down'

    def canPressDownvote(self, user):
        return self.userCanUpdownvote(user) or self.userHasUpdownvoted(user) == 'up'

    def isEditableBy(self, user):
        if not user.is_authenticated():
            return False
        if self.creator == user:
            return True
        if user.groups.filter(name__iexact="moderators"):
            return True
        return False

    def lastEdit(self):
        assert self.number_of_edits > 0, 'VotablePost.lastEdit() is irrelevant if number_of_edits == 0'
        return self.edit_history.latest('id')

    def cast(self):
        """ This method converts "self" into its correct child class
            More information: http://stackoverflow.com/a/13306529/1218058
        """
        for name in dir(self):
            try:
                attr = getattr(self, name)
                if isinstance(attr, self.__class__):
                    return attr
            except:
                pass
        return self


class UpDownVote(DisableableModel):
    """ An up- or downvote for a VotablePost.

    Note: These objects are immutable and irremovable so a reference to an UpDownVote never becomes obsolete.
          Instead of changing an UpDownVote, please disable it and make a new copy with the change.

    """
    # the '+' inhibits the creation of a updownvote_set in CustomUser (would not make sense because disabled objects are also in this list)
    user = models.ForeignKey(CustomUser, related_name="+")
    post = models.ForeignKey(VotablePost, related_name="up_down_votes_including_disabled")
    date = models.DateTimeField(auto_now_add=True)
    value = models.IntegerField(choices=((1, 'up'), (-1, 'down')))

class Tag(models.Model):
    """ A content tag that can be assigned to Proposals. """

    name = models.CharField(max_length=35)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

class VotablePostHistory(models.Model):
    """ Keeps track of changes to VotablePosts. """

    editing_user = models.ForeignKey(CustomUser)
    post = models.ForeignKey(VotablePost, related_name="edit_history")
    date = models.DateTimeField(auto_now_add=True)
    post_at_date = models.OneToOneField(VotablePost, related_name="history_object")

    class Meta:
        verbose_name = "VotablePost history"
        verbose_name_plural = "VotablePost histories"

    def __unicode__(self):
        post_str = truncatechars(unicode(self.post), 30)
        return "VotablePostHistory #{} for {}".format(self.number_of_previous_edits(), post_str)

    def number_of_previous_edits(self):
        return VotablePostHistory.objects.filter(post=self.post, date__lt=self.date).count()


class Proposal(VotablePost):
    """ Base class for all proposals.

    The main feature of a proposal is that it is subject to a voting process. This is not to
    be confused with up/downvoting, which is a different kind of voting, mainly used to indicate
    the popularity of a particular contribution.

    The voting process of a proposal has a begin and end date. It allows proxy voting (one user
    can let another user choose his/her vote).

    Note: it is possible to put constraints on the starting of the vote process (e.g. a minimal
          number of upvotes, in this case renamed to endorsements). These constraints are subject
          of debate and the current definition can be found in minimalContraintsAreMet().

    """
    # constants
    VOTING_STAGE = (
        ('DISCUSSION', 'Discussion'),
        ('VOTING', 'Voting'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
    )
    # fields
    title = models.CharField(max_length=255)
    slug = AutoSlugField(unique=True, populate_from='title')
    views = models.IntegerField(default=0)
    voting_stage = models.CharField(max_length=20, choices=VOTING_STAGE, default='DISCUSSION')
    voting_date = models.DateTimeField(default=None, null=True, blank=True)
    expire_date = models.DateTimeField(default=None, null=True, blank=True)
    discussion_time = models.IntegerField(default=7)
    tags = models.ManyToManyField(Tag, related_name="proposals")
    avgProposalvoteScore = models.FloatField("score", default=0.0)
    favorited_by = models.ManyToManyField(User, related_name="favorites", null=True, blank=True)
    allowed_groups = models.ManyToManyField(Group, null=True, blank=True) # if null, all users can vote for this proposal
    viewed_by =  models.ManyToManyField(CustomUser, null=True, blank=True)

    def to_string(self):
        return self.title

    def get_mutable_copy(self, save=True):
        """ [override] fix some problems that happen on copy """
        ### call super ###
        copy_obj = super(Proposal, self).get_mutable_copy(save=False)

        ### fix ManyToMany problems ###
        if save:
            copy_obj.save()
            copy_obj.tags.add(*self.tags.all())
            copy_obj.favorited_by.add(*self.favorited_by.all())
            copy_obj.allowed_groups.add(*self.allowed_groups.all())
            copy_obj.viewed_by.add(*self.viewed_by.all())
        else:
            raise NotImplementedError("get_mutable_copy can't work without saving because there are ManyToMany fields")
        return copy_obj

    @property
    def comments(self):
        return self.comments_including_disabled.filter(enabled=True)

    @property
    def popularity(self):
        """ [overridden] A numerical measure for how popular a proposal is. This defines the position in lists. """
        return 1000*self.totalvotescore + 100*self.comments.count() + self.views

    @property
    def proposaltype(self):
        raise NotImplementedError()

    @property
    def totalvotescore(self):
        if self.voting_stage in ['DISCUSSION']:
            return self.upvote_score
        else:
            return self.proposal_votes.count()

    @property
    def number_of_comments(self):
        return self.comments.count()

    @property
    def finishedVoting(self):
        return self.voting_stage == 'APPROVED' or self.voting_stage == 'REJECTED'

    @property
    def estimatedVotingDate(self):
        if self.voting_stage in ['EXPIRED', 'DISCUSSION']:
            nominal_date = self.create_date + datetime.timedelta(days=self.discussion_time)
            return nominal_date
        else:
            return self.voting_date

    @property
    def estimatedFinishDate(self):
        return self.estimatedVotingDate + datetime.timedelta(days=settings.VOTING_DAYS)

    @property
    def expirationDate(self):
        """ date the proposal expires because lack of interest """
        if self.minimalContraintsAreMet():
            return None
        return self.create_date + datetime.timedelta(days=self.discussion_time)

    def minimalNumEndorsementsIsMet(self):
        return self.upvote_score >= settings.MIN_NUM_ENDORSEMENTS_BEFORE_VOTING

    def minimalContraintsAreMet(self):
        """ True if non-date constraints are met """
        return self.minimalNumEndorsementsIsMet()

    def canBeVotedOnByUser(self, user):
        if self.allowed_groups.count():
            for group in self.allowed_groups.all():
                if group in user.groups.all():
                    return None
        else:
            return None
        return "This user is not a member in any of the required groups"

    @property
    def upvotesNeededBeforeVoting(self):
        """ True if non-date constraints are met """
        missing = settings.MIN_NUM_ENDORSEMENTS_BEFORE_VOTING - self.upvote_score
        return missing if missing >= 0 else 0

    def shouldStartVoting(self):
        # check relevance
        if self.voting_stage != 'DISCUSSION':
            return False
        # should start voting if start properties fullfilled
        shouldStartVoting = (timezone.now() > self.create_date + datetime.timedelta(days=self.discussion_time)
                            and
                            self.minimalContraintsAreMet())
        return shouldStartVoting

    def shouldBeFinished(self):
        # check relevance
        if self.voting_stage != 'VOTING':
            return False
        # should finish voting if end properties fullfilled
        shouldBeFinished = timezone.now() > self.voting_date + datetime.timedelta(days=settings.VOTING_DAYS)
        return shouldBeFinished

    def shouldExpire(self):
        return self.expirationDate and timezone.now() > self.expirationDate

    def isValidTitle(self, title):
        """ Check:
                * if the title already exists (case insensitive)
                * if the slug derived from title already exists,
            Keeps into account possibility of already existing object.
        """
        def is_empty_or_self(queryset):
            return queryset.count() == 0 or queryset[0].pk == self.pk
        return is_empty_or_self(Proposal.all_objects.filter(title__iexact=title)) \
            and is_empty_or_self(Proposal.all_objects.filter(slug=slugify(title)))

    def hasActed(self, user):
        if self.voting_stage in ['DISCUSSION']:
            return self.userHasUpdownvoted(user)
        else:
            return self.userHasProposalvoted(user)

    def hasCommented(self, user):
        if user.is_authenticated():
            return self.comments.filter(creator=user).count()
        return False

    def hasViewed(self, user):
        if user.is_authenticated():
            return self.viewed_by.filter(pk=user.pk).exists()
        return False

    def incrementViewCounter(self, user):
        self.views += 1
        if user.is_authenticated():
            self.viewed_by.add(user)
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
        return self.avgProposalvoteScore > 0 and self.proposal_votes.count() >= settings.QUORUM_SIZE

    def commentsAllowed(self):
        return (self.voting_stage == 'DISCUSSION' and settings.COMMENTS_IN_DISCUSSION) or (self.voting_stage == 'VOTING' and settings.COMMENTS_IN_VOTING) or (self.voting_stage in ['APPROVED','REJECTED','EXPIRED'] and settings.COMMENTS_IN_FINISHED)

    def commentsAllowedBy(self, user):
        return self.commentsAllowed() and (user.is_authenticated() or settings.ANONYMOUS_COMMENTS)

    def isEditableBy(self, user):
        if not super(Proposal, self).isEditableBy(user):
            return False
        return self.voting_stage in ['DISCUSSION']

    def execute(self):
        """ perform necessary actions upon isApproved() """
        pass

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
            ('5', 'For'),
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
            (voting, 250),
            (finish, 500),
            (finish + d10, 550),
        ]
        ## linear interpolation between fixed dates
        px = fixed_dateToPx[0][1]
        for (date1, px1), (date2, px2) in zip(fixed_dateToPx[:-1], fixed_dateToPx[1:]):
            if date1 <= date <= date2:
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
        a = self.final_proxy_proposal_votes.filter(value = vote_value, voted_self=True).aggregate(Sum('numvotes'))
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
        return self.final_proxy_proposal_votes.filter(value = vote_value, voted_self=True)


class AmendmentProposal(Proposal):
    """ Proposal for ammending a document.

    The main component of this kind of proposal is the 'diff'. This is a set of changes that is made
    to one of the documents (see document.models).

    """
    motivation = models.TextField()
    diff = models.ForeignKey(Diff)

    @property
    def diffWithContext(self):
        return self.diff.getNDiff()

    @property
    def proposaltype(self):
        return "amendment"

    def execute(self):
        try:
            if hasattr(self,'diff'):
                self.diff.fulldocument.getFinalVersion().applyDiff(self.diff)
            else:
                  "Proposal",self.title,"is approved, but has no Diff"
        except Exception as e:
            print traceback.format_exc()
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
                if hasattr(proposal,'diff'):
                    newdiff = proposal.diff.applyDiffOnThisDiff(self.diff)
                    newdiff.fulldocument = self.diff.fulldocument.getFinalVersion()
                    newdiff.save()
                    proposal.diff = newdiff
                    proposal.save()
                    # TODO: create history record
            except Exception as e:
                print "Error applying diff to other diffs: ", e
                print traceback.format_exc()
                # TODO: catch this in nice way


class PositionProposal(Proposal):
    """ Proposal for a position or statement that also can be used as a poll.

    The main component is a text on which the users can vote. This text is assumed to
    contain a statement as well as an (optional) motivation.

    """
    position_text = models.TextField()

    @property
    def proposaltype(self):
        return "position"


class Comment(VotablePost):
    """ Comment on a Proposal.

    Allows users to comment on proposals.

    """
    # constants
    COMMENT_COLORS = (
        ('POS', 'positive'),
        ('NEUTR', 'neutral'),
        ('NEG', 'negative'),
    )

    # fields
    proposal = models.ForeignKey(Proposal, related_name="comments_including_disabled")
    motivation = models.TextField()
    color = models.CharField(max_length=10, choices=COMMENT_COLORS, default='NEUTR')

    # methods
    def to_string(self):
        proposal = truncatechars(unicode(self.proposal), 30)
        motivation = truncatechars(self.motivation, 30)
        return "Comment on {}: {}".format(proposal, motivation)

    def isEditableBy(self, user):
        if not super(Comment, self).isEditableBy(user):
            return False
        return self.proposal.voting_stage in ['DISCUSSION']

    def truncated_motivation(self):
        return truncatechars(self.motivation, 30)
    truncated_motivation.short_description = "motivation"

class CommentReply(VotablePost):
    """ Reply on a Comment.

    Allows users to reply on comments on proposals.

    """
    # fields
    comment = models.ForeignKey(Comment, related_name="replies_including_disabled")
    motivation = models.TextField(validators=[
        MinLengthValidator(settings.COMMENTREPLY_MIN_LENGTH),
        MaxLengthValidator(settings.COMMENTREPLY_MAX_LENGTH),
    ])

    def to_string(self):
        return "Reply to comment on {}".format(self.comment.proposal)

    def isEditableBy(self, user):
        if not super(CommentReply, self).isEditableBy(user):
            return False
        return self.comment.proposal.voting_stage in ['DISCUSSION']

    def truncated_motivation(self):
        return truncatechars(self.motivation, 30)
    truncated_motivation.short_description = "motivation"


class ProposalVote(models.Model):
    """ Contains what the user entered on the website for his vote.

    This is not to be confused with an UpDownVote. This type of vote is exclusively used for the voting
    process of Proposals, with a distinct begin and end time.

    """
    user = models.ForeignKey(CustomUser, related_name="proposal_votes")
    proposal = models.ForeignKey(Proposal, related_name="proposal_votes")
    date = models.DateTimeField(auto_now_add=True)
    value = models.IntegerField("The value of the vote")


class ProxyProposalVote(models.Model):
    """ This contains where everybodies votes came from  and went to in effect, it is the voting matrix.

    Note: If the user_voting did not actually vote, the numvotes need to be interpreted as the number
    of votes "flowing through" this user, which is an upperbound to what the user would really have if
    he actually voted.

    """
    user_voting = models.ForeignKey(CustomUser, related_name="proxy_proposal_votes")
    user_proxied = models.ForeignKey(CustomUser, related_name="proxied_proposal_votes")
    proposal = models.ForeignKey(Proposal, related_name="proxy_proposal_votes")
    numvotes = models.FloatField(default=0)

    @property
    def getUpperBound(self):
        if numvotes>1.0:
            return 1.0
        return numvotes

    @property
    def getVoteOfVotingUser(self):
        return FinalProposalVote.objects.get(proposal=self.proposal, user=self.user_voting)


class FinalProposalVote(models.Model):
    """ This contains who voted what eventually after counting. """

    user = models.ForeignKey(CustomUser, related_name="final_proxy_proposal_votes")
    proposal = models.ForeignKey(Proposal, related_name="final_proxy_proposal_votes")
    numvotes = models.FloatField(default=0)
    value = models.FloatField(default=0)
    voted_self = models.BooleanField(help_text='If this is False, this vote actually went to other people.')

    @property
    def getProxyProposalVoteSources(self):
        return ProxyProposalVote.objects.filter(proposal=self.proposal, user_voting=self.user).all()

    @property
    def getProxyProposalVoteEndNodes(self):
        return ProxyProposalVote.objects.filter(proposal=self.proposal, user_proxied=self.user, user_voting__in=self.proposal.proposal_votes.values("user")).all()


class Proxy(DisableableModel):
    """ Object containing the issued proxies for the voting system.

    Note: These objects are immutable and irremovable so a reference to a Proxy never becomes obsolete.
          Instead of changing a Proxy, please disable it and make a new copy with the change.

    """
    # the '+' inhibits the creation of a proxy_set in CustomUser and Tag (would not make sense because disabled objects are also in this list)
    delegating = models.ForeignKey(CustomUser, related_name="+")
    delegates = models.ManyToManyField(CustomUser, related_name="+")
    tags = models.ManyToManyField(Tag, related_name="+")
    isdefault = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        delegates = ','.join(unicode(d) for d in self.delegates.all())
        delegates = truncatechars(delegates, 40)
        return "Proxy of {} to ({})".format(self.delegating, delegates)

    def tags_str(self):
        """ string representation of tags """
        tags = ','.join(unicode(d) for d in self.tags.all())
        tags = truncatechars(tags, 40)
        return tags
    tags_str.short_description = "tags"

    def get_mutable_copy(self, save=True):
        """ [override] fix some problems that happen on copy """
        # call super
        copy_obj = super(Proxy, self).get_mutable_copy(save=False)
        # fix date_created
        copy_obj.date_created = timezone.now()
        # fix ManyToMany problems
        if save:
            copy_obj.save()
            copy_obj.delegates.add(*self.delegates.all())
            copy_obj.tags.add(*self.tags.all())
        else:
            raise NotImplementedError("get_mutable_copy can't work without saving because there are ManyToMany fields")
        return copy_obj

    class Meta(DisableableModel.Meta):
        verbose_name_plural = "Proxies"
