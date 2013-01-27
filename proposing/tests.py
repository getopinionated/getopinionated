import datetime

from django.utils import timezone
from django.test import TestCase

from proposal.models import Proposal
from django.core.urlresolvers import reverse

class ProposalMethodTests(TestCase):

    def test_was_published_recently_with_future_poll(self):
        """
        was_published_recently() should return False for polls whose
        pub_date is in the future
        """
        future_proposal = Proposal(create_date=timezone.now() + datetime.timedelta(days=30))
        self.assertEqual(future_proposal.was_published_recently(), False)
        
        
def create_proposal(title, extra_days):
    """
    Creates a poll with the given `title` published the given number of
    `extra_days` offset to now (negative for polls published in the past,
    positive for polls that have yet to be published).
    """
    return Proposal.objects.create(title=title,
        create_date=timezone.now() + datetime.timedelta(days=extra_days))


'''
class ProposalViewTests(TestCase):
    def test_index_view_with_no_polls(self):
        """
        If no polls exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('proposal:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No proposals are available.")
        self.assertQuerysetEqual(response.context['latest_proposal_list'], [])

    def test_index_view_with_a_past_poll(self):
        """
        Polls with a pub_date in the past should be displayed on the index page.
        """
        create_proposal(title="Past proposal.", extra_days=-30)
        response = self.client.get(reverse('proposal:index'))
        self.assertQuerysetEqual(
            response.context['latest_proposal_list'],
            ['<Proposal: Past proposal.>']
        )

    def test_index_view_with_a_future_poll(self):
        """
        Polls with a pub_date in the future should not be displayed on the
        index page.
        """
        create_proposal(title="Future proposal.", extra_days=30)
        response = self.client.get(reverse('proposal:index'))
        self.assertContains(response, "No proposals are available.", status_code=200)
        self.assertQuerysetEqual(response.context['latest_proposal_list'], [])

    def test_index_view_with_future_poll_and_past_poll(self):
        """
        Even if both past and future polls exist, only past polls should be
        displayed.
        """
        create_proposal(title="Past proposal.", extra_days=-30)
        create_proposal(title="Future proposal.", extra_days=30)
        response = self.client.get(reverse('proposal:index'))
        self.assertQuerysetEqual(
            response.context['latest_proposal_list'],
            ['<Proposal: Past proposal.>']
        )

    def test_index_view_with_two_past_polls(self):
        """
        The polls index page may display multiple polls.
        """
        create_proposal(title="Past proposal 1.", extra_days=-30)
        create_proposal(title="Past proposal 2.", extra_days=-5)
        response = self.client.get(reverse('proposal:index'))
        self.assertQuerysetEqual(
            response.context['latest_proposal_list'],
             ['<Proposal: Past proposal 2.>', '<Proposal: Past proposal 1.>']
        )
        
'''