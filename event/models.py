import logging
from django.db import models
from django.utils import timezone
from common.utils import overrides
from accounts.models import CustomUser
from proposing.models import VotablePost, Proposal, VotablePostHistory, UpDownVote, Proxy

logger = logging.getLogger(__name__)

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
    def new_event_and_create_listeners_and_email_queue_entries(cls, listening_users, *args, **kwargs):
        """ Static factory for creating new events together with some related objects.

        Creates:
            - a new event of the given type, e.g.:
                VotablePostEditEvent.new_event_and_create_listeners_and_email_queue_entries(...)
            - a PersonalEventListener and PersonalEventEmailQueue for every listening_user
            - a GlobalEventEmailQueue if necessary

        Returns the new event, which is already saved. Returns None if the event and related objects are
        unnecessary (no global event and no listening_users).

        """
        # check that we are not trying to create an Event (instead of a subclass)
        if cls == Event:
            raise Exception("Call this method only on subclasses of Event.")

        # check necessity
        if len(listening_users) == 0 and not cls().is_global_event():
            return None

        # create new event
        event = cls(*args, **kwargs)
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
    viewed_by_user = models.BooleanField(default=False)

    def __unicode__(self):
        return u"PersonalEventListener: {} listens to {}".format(self.user, self.event)


class PersonalEventEmailQueue(models.Model):
    """ All objects of this model are temporarily queued until either an email gets sent to the user or an email
    turns out to be unnecessary/unwanted.

    Note: a PersonalEventEmailQueue object should be removed as soon as the email has been sent.
    Note2: emails can be queued also if user doesn't want any emails, this has to be filtered later.
    Note3: if the PersonalEventListener.viewed_by_user is True, no email has to be sent.

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


class VotablePostEditEvent(Event):
    """ A VotablePost was edited """

    edit = models.ForeignKey(VotablePostHistory)

    @overrides(Event)
    def is_global_event(self):
        return False

    @overrides(Event)
    def __unicode__(self):
        return u"VotablePostEditEvent for {}".format(self.edit)


class ProposalForkEvent(Event):
    """ An existing origin_proposal was forked. """

    origin_proposal = models.ForeignKey(Proposal, related_name="+fork_event_origin")
    fork_proposal = models.ForeignKey(Proposal, related_name="+fork_event")

    @overrides(Event)
    def is_global_event(self):
        return False

    @overrides(Event)
    def __unicode__(self):
        return u"ProposalForkEvent: forked {}".format(self.origin_proposal)


class UpDownVoteEvent(Event):
    """ A VotablePost was up- or downvoted """

    updownvote = models.ForeignKey(UpDownVote)

    @overrides(Event)
    def is_global_event(self):
        return False

    @overrides(Event)
    def __unicode__(self):
        return u"UpDownVoteEvent for {}".format(self.updownvote)


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

