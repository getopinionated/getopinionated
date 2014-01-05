import re
import logging
from collections import OrderedDict
from django import template
from django.utils.safestring import mark_safe
from event.models import Event

logger = logging.getLogger('event')
register = template.Library()

class BundledEvent:
    """ Contains all information to generate a bundled representation of a set of events """
    events = None
    unseen_events = False
    user = None

    def __init__(self, events, unseen_events, user):
        """ Constructor.

        Arguments:
        events -- List of mutually combinable events that are bundled. Their ordering does not matter as they will
                  be sorted.
        unseen_events -- List of unseen events. May contain events that are irrelevant.
        user -- the user that will be looking at the event.

        """
        self.events = sorted(events, key=lambda e: e.date_created)
        self.unseen_events = unseen_events
        self.user = user

    def html_string(self):
        try:
            return mark_safe(Event.generate_html_string_for(self.events, self.user))
        except:
            import traceback
            logger.warning(traceback.format_exc())
            return "<<ERROR>>"

    def contains_unseen_events(self):
        return any(e in self.unseen_events for e in self.events)

    def __unicode__(self):
        return u"BundledEvent for {}".format(self.events)

@register.filter(name='listeners_to_bundled_events')
def listeners_to_bundled_events(personal_event_listeners, max_num_of_bundles=None):
    """ Bundles PersonalEventListeners into a list of combined events for use in a notification bar or emails.

    Arguments:
    personal_event_listeners -- should be a models.Manager.
    max_num_of_bundles -- The maximum number of BundledEvents to return in case seen events are also returned. If
                          not specified, only unseen BundledEvent are returned.

    Returns:
    List of BundledEvent objects.

    """
    def _get_events(seen_by_user):
        event_listeners = personal_event_listeners.filter(seen_by_user=seen_by_user).order_by('-event__date_created')
        return [listener.event.cast() for listener in event_listeners]

    def _combine_events_where_possible(events):
        """ Combine events where possible, keeping the original ordering (the first occurence of combined events remain ordered).

        Returns a list of event-lists which are mutually combinable.

        """
        combine_candidates = events
        result = [] # list of event-lists
        while combine_candidates:
            event = combine_candidates[0]
            # get combineable events
            combinable_events = [event_cand for event_cand in combine_candidates if event.can_be_combined_with(event_cand, user)]
            assert event in combinable_events, "reflexivity is violated"
            result.append(combinable_events)
            # update candidates
            combine_candidates = [e for e in combine_candidates if e not in combinable_events]
        return result

    def _add_event_to_combined_events(combined_events, event):
        for bundle in combined_events:
            if bundle[0].can_be_combined_with(event, user):
                bundle.append(event)
                break
        else:
            combined_events.append([event])
        return combined_events

    ## get user
    if not personal_event_listeners or personal_event_listeners.count() == 0:
        return
    user = personal_event_listeners.latest('pk').user

    ## Step 1: combine unseen_events
    unseen_events = _get_events(seen_by_user=False)
    combined_events = _combine_events_where_possible(unseen_events)

    ## Step 2: add seen events untill max_num_of_bundles is reached
    seen_events = _get_events(seen_by_user=True)
    for event in seen_events:
        if max_num_of_bundles is None or len(combined_events) >= max_num_of_bundles:
            break
        else:
            combined_events = _add_event_to_combined_events(combined_events, event)

    ## Step 3: generate BundledEvent from combined_events
    for combination in combined_events:
        yield BundledEvent(
            events=combination,
            unseen_events=unseen_events,
            user=user,
        )

    # return [mark_safe("<b>{}</b><br>".format(unicode(l))) for l in personal_event_listeners.all()]
