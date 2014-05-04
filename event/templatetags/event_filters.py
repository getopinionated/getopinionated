import re
import logging
from collections import OrderedDict
from django import template
from django.utils.safestring import mark_safe
from common.utils import deprecated
from event.models import Event

logger = logging.getLogger('event')
register = template.Library()

class BundledEvent:
    """ Contains all information to generate a bundled representation of a set of events """
    events = None
    unseen_events = None
    reading_user = None
    human_readable_text = ""
    link_url = ""

    def __init__(self, events, unseen_events, reading_user):
        """ Constructor.

        Arguments:
        events -- List of mutually combinable events that are bundled. Their ordering does not matter as they will
                  be sorted.
        unseen_events -- List of unseen events. May contain events that are irrelevant.
        reading_user -- the user that will be looking at the event.

        """
        self.events = sorted(events, key=lambda e: e.date_created)
        self.unseen_events = unseen_events
        self.reading_user = reading_user
        self.human_readable_text, self.link_url = Event.generate_human_readable_format(self.events, self.reading_user)

    @deprecated
    def html_string(self):
        try:
            return mark_safe(Event.generate_html_string_for(self.events, self.reading_user))
        except:
            import traceback
            logger.warning(traceback.format_exc())
            return "<<ERROR>>"

    def contains_unseen_events(self):
        return any(e in self.unseen_events for e in self.events)

    def __repr__(self):
        return "BundledEvent for {}".format(self.events)
    
    def __unicode__(self):
        return u"BundledEvent for {}".format(self.events)

@register.filter(name='listeners_to_bundled_events')
def listeners_to_bundled_events(personal_event_listeners, max_num_of_bundles=None):
    """ Bundles PersonalEventListeners into a list of combined events for use in a notification bar or emails.

    Arguments:
    personal_event_listeners -- should be a models.Manager or a list.
    max_num_of_bundles -- The maximum number of BundledEvents to return in case seen events are also returned. If
                          not specified, only unseen BundledEvent are returned.

    Returns:
    List of BundledEvent objects.

    """
    def _get_events(seen_by_user):
        # get events with seen_by_user == seen_by_user
        event_listeners = sorted([p for p in personal_event_listeners if p.seen_by_user == seen_by_user], lambda p: -p.event.date_created)
        events = [listener.event.cast() for listener in event_listeners]

        # filter deprecated events
        events = [event for event in events if not event.is_deprecated(user)]
        return events


    def _combine_events_where_possible(events):
        """ Combine events where possible, keeping the original ordering (the first occurence of combined events remain ordered).

        Returns a list of event-lists which are mutually combinable.

        """
        combine_candidates = events
        result = [] # list of event-lists
        while combine_candidates:
            event = combine_candidates[0]
            # get combineable events
            combinable_events = [event_cand for event_cand in combine_candidates if \
                type(event) == type(event_cand) and event.can_be_combined_with(event_cand, user)]
            assert event in combinable_events, "reflexivity is violated"
            result.append(combinable_events)
            # update candidates
            combine_candidates = [e for e in combine_candidates if e not in combinable_events]
        return result

    def _add_event_to_combined_events(combined_events, event):
        for bundle in combined_events:
            if type(bundle[0]) == type(event) and bundle[0].can_be_combined_with(event, user):
                bundle.append(event)
                break
        else:
            combined_events.append([event])
        return combined_events

    # convert personal_event_listeners to a list
    personal_event_listeners = [p for p in personal_event_listeners] if personal_event_listeners else []
    if not personal_event_listeners:
        return []

    ## get user
    user = personal_event_listeners[0].user

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
    result = []
    for combination in combined_events:
        result.append(BundledEvent(
            events=combination,
            unseen_events=unseen_events,
            reading_user=user,
        ))
    return result

@register.filter(name='cached_events')
def cached_events(user):
    """Calls the more versatile filter listeners_to_bundled_events to generate max 10 bundles and caches
    the result.

    """
    if hasattr(user, '_cached_events'):
        return user._cached_events

    result = listeners_to_bundled_events(
        personal_event_listeners=user.personal_event_listeners,
        max_num_of_bundles=10,
    )
    user._cached_events = result
    return result

@register.filter(name='count_unseen_bundledevents')
def count_unseen_bundledevents(bundledevents):
    """Return the number of BundledEvents in bundledevents that respond True to contains_unseen_events()."""
    return len([b for b in bundledevents if b.contains_unseen_events()])
