import logging
from django.db import models
from django.utils import timezone
from django.template.defaultfilters import truncatechars, pluralize
from common.utils import overrides, deprecated
from common.templatetags.filters import userjoin
from accounts.models import CustomUser
from utils import url_to, add_owner, wrap_html_link_to, get_owner_str, link_and_add_owner
from proposing.models import VotablePost, Comment, CommentReply, Proposal, VotablePostHistory, UpDownVote, Proxy

logger = logging.getLogger(__name__)

def _everyone_except(listening_users, event_causing_user):
    """ small utility method for use in event.get_listening_users() """
    return set([u for u in listening_users if u != event_causing_user])

class Event(models.Model):
    """ Base class for all events on the site that might be of interest for someone.

    Defenition of personal and global events:
    These events (like a reply to a comment) can be interesting only for one or a few number of users. These
    are called "personal events". Other events (like the start of a vote) can be interesting for all users of
    the site, which are called "global events". Note that global events can be personal events too (e.g.: the
    start of a vote is a global event but you might only want an email about if you endorsed this proposal)

    Note: this model defines the properties of an event but does not distinguish between personal and global,
          nor does it contain a link to a particular user. This is done in PersonalEventListener.

    """
    date_created = models.DateTimeField(auto_now_add=True)

    def is_global_event(self):
        """ Return True if this event can be of interest for every user. This means that it will be added to the
        GlobalEventEmailQueue.

        Make sure to override this in every child.

        """
        raise NotImplementedError("Every Event implementation should override this method.")

    def can_be_combined_with(self, event, reading_user):
        """ Return True if self can be combined with event into one string. This means that generate_human_readable_format
        would succeed on [self, event].

        Note: can_be_combined_with can only be called with an event of the same class as self.

        This method defines a relationship between events that should be:
            - Reflexive: x.can_be_combined_with(x) should return True.
            - Symmetric: x.can_be_combined_with(y) should return True if and only if y.can_be_combined_with(x) returns
                         True.
            - Transitive: If x.can_be_combined_with(y) returns True and y.can_be_combined_with(z) returns True, then
                          x.can_be_combined_with(z) should return true.

        Arguments:
        event -- an instance of the same subclass of Event as self is.
        reading_user -- the user that will be looking at the event.

        Make sure to override this in every child.

        """
        raise NotImplementedError("Every Event implementation should override this method.")

    def is_deprecated(self, reading_user):
        """ Return True if this Event no longer has any relevance for reading_user. It will not be shown in reading_user's
        notification bar or emails.

        Arguments:
        reading_user -- the user that will be looking at the event.

        """
        return False

    def get_listening_users(self):
        """ Return a set of CustomUsers that should be notified about this event. Don't forget to remove the user that caused
        the event from the list.

        Note: after calling this method, None should always be filtered out of the list, so implementations of get_listening_users()
              don't have to bother checking for e.g. anonymous VotablePosts.

        Make sure to override this in every child.

        """
        raise NotImplementedError("Every Event implementation should override this method.")

    @staticmethod
    def generate_human_readable_format(events, reading_user):
        """ Return two strings (human_readable_text, link_url) that are a human readable representation of the given events
        combines events.

        Arguments:
        events -- should be mutually combinable (see can_be_combined_with()).
        reading_user -- the user that will be looking at the string.

        Returns:
        human_readable_text -- a textual summary of events for reading_user, containing regular text (e.g.: no html)
        link_url -- the most relevant link to these combined events

        Make sure to override this in every child.

        """
        ## sanity checks
        # check that all events are of the same class
        first = events[0]
        assert all(type(first) == type(e) for e in events), 'all events must be of the same class'
        # check that all events are combineable
        assert all(first.can_be_combined_with(e, reading_user) for e in events), 'all events must be mutually combineable'

        ## delegate generation to subclass
        # check if event is not instance of Event
        eventclass = type(first)
        if eventclass == Event:
            warning_msg = u"Event.generate_human_readable_format() should be overridden by every Event child. If you get this error, it is " + \
                u"possible that you have a database row with an Event (id={}) without a corresponding subclass. ".format(first.pk)  +  \
                u"You can verify this by going to the Event admin."
            logger.warning(warning_msg)
            return u"<<ILLEGAL Events with pks={}>>".format([e.pk for e in events])

        # check if generate_human_readable_format() has been implemented in the subclass
        elif eventclass.generate_human_readable_format == Event.generate_human_readable_format:
            raise NotImplementedError("Every Event implementation should override this method.")

        else:
            retval = eventclass.generate_human_readable_format(events, reading_user)
            assert retval != None and len(retval) == 2
            return retval

    def __unicode__(self):
        """ Make sure to override this in every child. """
        # fist try to cast self to the correct type
        if type(self) == Event:
            castedself = self.cast()
            if castedself != self:
                return castedself.__unicode__()

        warning_msg = u"Event.__unicode__() should be overridden by every Event child. If you get this error, it is " + \
            u"possible that you have a database row with an Event (id={}) without a corresponding subclass. ".format(self.pk)  +  \
            u"You can verify this by going to the Event admin."
        logger.warning(warning_msg)
        return u"<<ILLEGAL Event with pk={}>>".format(self.pk)

    @classmethod
    def new_event_and_create_listeners_and_email_queue_entries(cls, *args, **kwargs):
        """ Static factory method for creating new events together with some related objects.

        Creates:
            - a new event of the given type, e.g.:
                VotablePostEditEvent.new_event_and_create_listeners_and_email_queue_entries(...)
            - a PersonalEventListener and PersonalEventEmailQueue for every listening_user*
            - a GlobalEventEmailQueue if necessary
        * listening_users are those returned by event.get_listening_users()

        Returns the new event, which is already saved. Returns None if the event and related objects are
        unnecessary (no global event and no listening_users).

        """
        # check that we are not trying to create an Event (instead of a subclass)
        if cls == Event:
            raise Exception("Call this method only on subclasses of Event.")

        # get listening users
        event = cls(*args, **kwargs)
        listening_users = event.get_listening_users()
        listening_users = set(u for u in listening_users if u != None) # filter possible null entries

        # check necessity
        if len(listening_users) == 0 and not event.is_global_event():
            return None

        # create new event
        event.save()

        # create PersonalEventListeners and PersonalEventEmailQueues
        for listening_user in listening_users:
            # create PersonalEventListener
            listener = PersonalEventListener(
                event=event,
                user=listening_user,
            )
            listener.save()

            # create PersonalEventEmailQueue
            queue_entry = PersonalEventEmailQueue(
                event_listener=listener,
            )
            queue_entry.save()

        # create GlobalEventEmailQueue if necessary
        if event.is_global_event():
            GlobalEventEmailQueue(event=event).save()

        return event

    def cast(self, depth=1):
        """ This method converts "self" into its correct child class
            More information: http://stackoverflow.com/a/13306529/1218058

            The depth is used because more than one layer of inheritance is present. The depth is this maximal level.
        """
        for name in dir(self):
            try:
                attr = getattr(self, name)
                if isinstance(attr, self.__class__):
                    if depth > 1:
                        return attr.cast(depth=depth-1)
                    else:
                        return attr
            except:
                pass
        return self


class PersonalEventListener(models.Model):
    """ Ties an Event to a CustomUser.

    These are the events that appear in the event bar.

    """
    event = models.ForeignKey(Event, related_name="personal_event_listeners")
    user = models.ForeignKey(CustomUser, related_name="personal_event_listeners")
    seen_by_user = models.BooleanField(default=False)

    def __unicode__(self):
        return u"PersonalEventListener: {} listens to {}".format(self.user, self.event)


class PersonalEventEmailQueue(models.Model):
    """ All objects of this model are temporarily queued until either an email gets sent to the user or an email
    turns out to be unnecessary/unwanted.

    Note: a PersonalEventEmailQueue object should be removed as soon as the email has been sent.
    Note2: emails can be queued also if user doesn't want any emails, this has to be filtered later.
    Note3: if the PersonalEventListener.seen_by_user is True, no email has to be sent.

    """
    event_listener = models.OneToOneField(PersonalEventListener, related_name="queued_email")

    def __unicode__(self):
        return u"PersonalEventEmailQueue for {}".format(self.event_listener)


class GlobalEventEmailQueue(models.Model):
    """ All objects of this model are temporarily queued until all users that want to be emailed about the event
    have received an email.

    Note: a GlobalEventEmailQueue object should be removed as soon as there are no more emails that can be
          sent (i.e.: after the weekly digest).

    """
    event = models.ForeignKey(Event, related_name="queued_global_event_emails")
    already_mailed_users = models.ManyToManyField(CustomUser, related_name="sent_global_emails")

    def __unicode__(self):
        return u"GlobalEventEmailQueue for {}".format(self.event)


######### specific implementations of Events #########

class VotablePostReactionEvent(Event):
    """ A new VotablePost was made as reaction to another VotablePost. """

    origin_post = models.ForeignKey(VotablePost, related_name="+reaction_event_origin")
    reaction_post = models.ForeignKey(VotablePost, related_name="+reaction_event")

    @overrides(Event)
    def is_global_event(self):
        return False

    @overrides(Event)
    def __unicode__(self):
        return u"VotablePostReactionEvent to {}".format(self.origin_post)

    @overrides(Event)
    def can_be_combined_with(self, event, reading_user):
        return self.origin_post == event.origin_post

    @overrides(Event)
    def get_listening_users(self):
        ## get vars and add most obvious users
        origin_post = self.origin_post.cast()
        event_causing_user = self.reaction_post.creator
        listening_users = set([origin_post.creator])

        ## add others less obvious users
        if isinstance(origin_post, Proposal):
            # add everyone else who commented, replied to a comment or favorited this proposal
            proposal = origin_post
            for comment in proposal.comments:
                listening_users.add(comment.creator)
                for commentreply in comment.replies:
                    listening_users.add(commentreply.creator)
            for u in proposal.favorited_by.all():
                listening_users.add(u)

        elif isinstance(origin_post, Comment):
            # add everyone else who replied to this comment or favorited this proposal
            comment = origin_post
            for commentreply in comment.replies:
                listening_users.add(commentreply.creator)
            for u in comment.proposal.favorited_by.all():
                listening_users.add(u)

        return _everyone_except(listening_users, event_causing_user)

    @staticmethod
    @overrides(Event)
    def generate_human_readable_format(events, reading_user):
        # get vars
        origin_post = events[0].origin_post.cast()
        users = userjoin(e.reaction_post.creator for e in events)
        origin_post_str = add_owner(origin_post, reading_user)
        link_target_post = events[0].reaction_post.cast() if len(events) == 1 else origin_post

        # return description + url
        return u"{} reacted to {}".format(users, origin_post_str), url_to(link_target_post)


class ProxyChangeEvent(Event):
    """ A proxy has been added or removed.

    Note: only 'ADDED' should be supported because 'REMOVED' seems like an unpleasant message (analogy: facebook only
          notifies you when someone accepted your friend request but never notifies about defriending). 'REMOVED' was
          added for completeness.

    """
    # constants
    CHANGE_TYPES = (
        ('ADDED', 'Added'),
        ('REMOVED', 'Removed'),
    )

    # fields
    change_type = models.CharField(max_length=10, choices=CHANGE_TYPES)
    new_proxy = models.ForeignKey(Proxy)

    @overrides(Event)
    def is_global_event(self):
        return False

    @overrides(Event)
    def __unicode__(self):
        return u"ProxyChangeEvent: {} {}".format(self.get_change_type_display(), self.new_proxy)

    @overrides(Event)
    def can_be_combined_with(self, event, reading_user):
        raise NotImplementedError("TODO")


class ProposalLifeCycleEvent(Event):
    """ A proposal was created or the voting stage of a Proposal has changed. """

    proposal = models.ForeignKey(Proposal)
    new_voting_stage = models.CharField(max_length=20, choices=Proposal.VOTING_STAGE)

    @overrides(Event)
    def is_global_event(self):
        return True

    @overrides(Event)
    def __unicode__(self):
        return u"ProposalLifeCycleEvent: {} -> {}".format(self.proposal, self.get_new_voting_stage_display())

    @overrides(Event)
    def can_be_combined_with(self, event, reading_user):
        return self == event

    @overrides(Event)
    def get_listening_users(self):
        ## get vars and add most obvious users
        proposal = self.proposal
        listening_users = set([proposal.creator])

        ## add others less obvious users:
        # add everyone else who commented or replied to a comment
        for comment in proposal.comments:
            listening_users.add(comment.creator)
            for commentreply in comment.replies:
                listening_users.add(commentreply.creator)

        # add everyone else who favorited this proposal
        for u in proposal.favorited_by.all():
            listening_users.add(u)

        if self.new_voting_stage == 'DISCUSSION':
            return _everyone_except(listening_users, proposal.creator)
        else:
            return listening_users

    @staticmethod
    @overrides(Event)
    def generate_human_readable_format(events, reading_user):
        # get vars
        assert len(events) == 1, "combining ProposalLifeCycleEvents not (yet) supported"
        proposal = events[0].proposal.cast()
        new_voting_stage = events[0].new_voting_stage

        # prepare strings
        proposal_str = add_owner(proposal, reading_user)
        url = url_to(proposal)
        creator_str = unicode(proposal.creator) if proposal.creator != None else u'Someone'

        # return full combination
        if new_voting_stage == 'DISCUSSION':
            return u"{} made a new proposal: {}".format(creator_str, proposal.title), url

        elif new_voting_stage == 'VOTING':
            return u"Voting started for {}".format(proposal_str), url

        elif new_voting_stage == 'APPROVED':
            return u"{} was approved".format(proposal_str), url

        elif new_voting_stage == 'REJECTED':
            return u"{} was rejected".format(proposal_str), url

        elif new_voting_stage == 'EXPIRED':
            return u"{} expired".format(proposal_str), url

        else:
            raise NotImplementedError("Unknown voting stage " + new_voting_stage)


class UpDownVoteEvent(Event):
    """ A VotablePost was up- or downvoted.

    Please note that removal of a vote is not seen as an UpDownVoteEvent. Also, a, UpDownVote that has been disabled is
    immediately deprecated.

    """
    updownvote = models.ForeignKey(UpDownVote)

    @overrides(Event)
    def is_global_event(self):
        return False

    @overrides(Event)
    def __unicode__(self):
        return u"UpDownVoteEvent for {}".format(self.updownvote)

    @overrides(Event)
    def is_deprecated(self, reading_user):
        return not self.updownvote.enabled

    @overrides(Event)
    def can_be_combined_with(self, event, reading_user):
        return self.updownvote.post == event.updownvote.post

    @overrides(Event)
    def get_listening_users(self):
        ## only the creator of updownvote.post is a listening_user
        return set([self.updownvote.post.creator])

    @staticmethod
    @overrides(Event)
    def generate_human_readable_format(events, reading_user):
        # get vars
        post = events[0].updownvote.post.cast()
        post_str = add_owner(post, reading_user)
        users = userjoin(e.updownvote.user for e in events)
        url = url_to(post)

        # get net increase / decrease in score
        score_diff = sum(e.updownvote.value for e in events)

        # return full combination
        if isinstance(post, Proposal):
            return u"{} got {} endorsement{} by {}".format(post_str, score_diff, pluralize(score_diff), users), url
        elif score_diff >= 0:
            return u"{} got {} upvote{}".format(post_str, score_diff, pluralize(score_diff)), url
        else:
            score_diff = abs(score_diff)
            return u"{} got {} downvote{}".format(post_str, score_diff, pluralize(score_diff)), url
