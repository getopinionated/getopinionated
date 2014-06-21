import os
import re
from collections import OrderedDict

from django.test import TestCase
from django.core.management import call_command
from django.utils import timezone
from django.utils.timezone import datetime, timedelta
from django.core import mail
from django.test import Client

from proposing.models import PositionProposal, Comment
from event.models import Event, ProposalLifeCycleEvent, UpDownVoteEvent, VotablePostReactionEvent, GlobalEventEmailQueue
from accounts.models import CustomUser

class SendEmailTestCase(TestCase):

    users = None
    proposals = None

    def setUp(self):
        ### helper methods ###
        def make_user(username, **kwargs):
            u = CustomUser(username=username, email="{}@test.org".format(username), **kwargs)
            u.save()
            self.users[username] = u

        def make_proposal(name, **kwargs):
            proposal = PositionProposal(
                title=name,
                slug=name,
                position_text="{} text".format(name),
                **kwargs
            )
            proposal.save()
            self.proposals[name] = proposal
            ProposalLifeCycleEvent.new_event_and_create_listeners_and_email_queue_entries(
                proposal=proposal,
                new_voting_stage='DISCUSSION',
            )

        def make_comment(proposal_id, user, **kwargs):
            comment = Comment(
                creator=user,
                proposal=self.proposals[proposal_id],
                motivation="comment by {}".format(user.username),
            )
            comment.save()
            VotablePostReactionEvent.new_event_and_create_listeners_and_email_queue_entries(
                origin_post=self.proposals[proposal_id],
                reaction_post=comment,
            )

        ### set up users ###
        self.users = OrderedDict()
        make_user('user0', mail_frequency='IMMEDIATELY', mail_when_voting_stage_change='ALWAYS', mail_when_related_event=True)
        make_user('user1', mail_frequency='DAILY', mail_when_voting_stage_change='ALWAYS', mail_when_related_event=True)
        make_user('user2', mail_frequency='DAILY', mail_when_voting_stage_change='ALWAYS', mail_when_related_event=False)
        make_user('user3', mail_frequency='DAILY', mail_when_voting_stage_change='I_REACTED', mail_when_related_event=False)
        make_user('user4', mail_frequency='DAILY', mail_when_voting_stage_change='I_STARRED', mail_when_related_event=False)
        make_user('user5', mail_frequency='DAILY', mail_when_voting_stage_change='NEVER', mail_when_related_event=True)
        make_user('user6', mail_frequency='DAILY', mail_when_voting_stage_change='NEVER', mail_when_related_event=False)
        make_user('user7', mail_frequency='WEEKLY', mail_when_voting_stage_change='ALWAYS', mail_when_related_event=True)

        ### set up proposals ###
        self.proposals = OrderedDict()
        make_proposal('proposal0', creator=self.users['user0'])
        make_proposal('proposal1', creator=self.users['user0'])
        make_proposal('proposal2', creator=self.users['user0'])

        # add favorites
        for user in self.users.values():
            self.proposals['proposal1'].favorited_by.add(user)

        # add reactions
        for user in self.users.values():
            make_comment('proposal2', user)

        # progress voting stage
        def progress_voting_stage(proposal_id, new_voting_stage):
            self.proposals[proposal_id].voting_stage = new_voting_stage
            self.proposals[proposal_id].save()
            ProposalLifeCycleEvent.new_event_and_create_listeners_and_email_queue_entries(
                proposal=self.proposals[proposal_id],
                new_voting_stage=new_voting_stage,
            )
        progress_voting_stage('proposal1', 'VOTING')
        progress_voting_stage('proposal2', 'EXPIRED')

    def _assert_num_bundled_events_in_mail(self, mail_object, num_bundled_events):
        """ checks whether the number of bundledevents that are shown in the given mail are equal to num_bundled_events """
        num_bundled_events_in_mail = mail_object.body.count('- ')
        self.assertEquals(num_bundled_events_in_mail, num_bundled_events, "Got {} bundledevents, but expected {} in:\n{}\n\n".format(
            num_bundled_events_in_mail, num_bundled_events, mail_object.body))

    def _print_email_body(self, mail_object):
        print "============================ EMAIL ============================="
        print mail.outbox[0].body
        print "========================= END OF EMAIL ========================="
        print

    def test_all(self):
        """ all individual tests should still work if they are performed in one test """
        self.test_send_mail_immediately()
        self.test_send_mail_daily()
        self.test_send_mail_weekly()

    def test_send_mail_immediately(self):
        mail.outbox = [] # empty the test outbox
        call_command('sendeventmails', 'IMMEDIATELY', stdout=open(os.devnull, 'w'))
        self.assertEquals(len(mail.outbox), 1)
        self._assert_num_bundled_events_in_mail(mail.outbox[0], 5 + 1) # global + personal
        #self._print_email_body(mail.outbox[0])
        
        mail.outbox = [] # empty the test outbox
        call_command('sendeventmails', 'IMMEDIATELY', stdout=open(os.devnull, 'w'))
        self.assertEquals(len(mail.outbox), 0)

    def test_send_mail_daily(self):
        mail.outbox = [] # empty the test outbox
        call_command('sendeventmails', 'DAILY', stdout=open(os.devnull, 'w'))
        self.assertEquals(len(mail.outbox), 5)
        self._assert_num_bundled_events_in_mail(mail.outbox[0], 5 + 1) # global + personal (user1)
        self._assert_num_bundled_events_in_mail(mail.outbox[1], 5 + 0) # global + personal (user2)
        self._assert_num_bundled_events_in_mail(mail.outbox[2], 2 + 0) # global + personal (user3)
        self._assert_num_bundled_events_in_mail(mail.outbox[3], 1 + 0) # global + personal (user4)
        self._assert_num_bundled_events_in_mail(mail.outbox[4], 0 + 3) # global + personal (user5)
        #self._print_email_body(mail.outbox[0])
        
        mail.outbox = [] # empty the test outbox
        call_command('sendeventmails', 'DAILY', stdout=open(os.devnull, 'w'))
        self.assertEquals(len(mail.outbox), 0)

    def test_send_mail_weekly(self):
        mail.outbox = [] # empty the test outbox
        call_command('sendeventmails', 'WEEKLY', stdout=open(os.devnull, 'w'))
        self.assertEquals(len(mail.outbox), 1)
        self._assert_num_bundled_events_in_mail(mail.outbox[0], 5 + 0) # global + personal
        
        mail.outbox = [] # empty the test outbox
        call_command('sendeventmails', 'WEEKLY', stdout=open(os.devnull, 'w'))
        self.assertEquals(len(mail.outbox), 0)

    def test_cleanup_globaleventemailqueue(self):
        original_num_globals = GlobalEventEmailQueue.objects.count()

        ## call sendeventmails with no expired global events
        queueitem0 = GlobalEventEmailQueue.objects.all()[:1].get()
        event0 = queueitem0.event
        event0.date_created = timezone.now() - timedelta(days=6.75)
        event0.save()
        call_command('sendeventmails', 'IMMEDIATELY', stdout=open(os.devnull, 'w'))
        self.assertEquals(GlobalEventEmailQueue.objects.count(), original_num_globals)

        ## call sendeventmails with one expired global event
        queueitem1 = GlobalEventEmailQueue.objects.all()[1:2].get()
        event1 = queueitem1.event
        event1.date_created = timezone.now() - timedelta(days=7.75)
        event1.save()
        call_command('sendeventmails', 'IMMEDIATELY', stdout=open(os.devnull, 'w'))
        self.assertEquals(GlobalEventEmailQueue.objects.count(), original_num_globals - 1)
        self.assertEquals(GlobalEventEmailQueue.objects.filter(pk=queueitem1.pk).count(), 0)

    def test_unscribe(self):
        mail.outbox = [] # empty the test outbox
        call_command('sendeventmails', 'DAILY', stdout=open(os.devnull, 'w'))
        self.assertEquals(len(mail.outbox), 5)
        self._assert_num_bundled_events_in_mail(mail.outbox[0], 5 + 1) # global + personal (user1)
        mailcontent_user1 = mail.outbox[0].body # mail for user1
        assert 'user1' in mailcontent_user1

        # get unscribe link (e.g.: "/accounts/unsubscribe/mail/10232297444037157797/")
        unscribe_link = re.search(r'/accounts/unsubscribe/mail/\d+/', mailcontent_user1).group(0)

        # call unscribe link
        response = Client().get(unscribe_link)
        assert response.status_code == 200
        
        # check if user is unscribed
        user1 = CustomUser.objects.get(username='user1')
        assert user1.mail_frequency == 'NEVER', "The mail frequency of unscribed user is {}".format(user1.mail_frequency)

