from collections import OrderedDict

from django.test import TestCase
from django.core.management import call_command
from django.core import mail

from proposing.models import PositionProposal, Comment
from event.models import ProposalLifeCycleEvent, UpDownVoteEvent, VotablePostReactionEvent
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
        make_user('user1', mail_frequency='DAILY', mail_when_voting_stage_change='ALWAYS', mail_when_related_event=False)
        make_user('user2', mail_frequency='DAILY', mail_when_voting_stage_change='ALWAYS', mail_when_related_event=True)
        make_user('user3', mail_frequency='DAILY', mail_when_voting_stage_change='I_REACTED', mail_when_related_event=True)
        make_user('user4', mail_frequency='DAILY', mail_when_voting_stage_change='I_STARRED', mail_when_related_event=True)
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
        self.assertEquals(mail_object.body.count('- '), num_bundled_events)

    def _print_email_body(self, mail_object):
        print "============================ EMAIL ============================="
        print mail.outbox[0].body
        print "========================= END OF EMAIL ========================="
        print

    def test_send_mail_immediately(self):
        mail.outbox = [] # Empty the test outbox
        call_command('senddigestmails', 'IMMEDIATELY')
        self.assertEquals(len(mail.outbox), 1)
        self._assert_num_bundled_events_in_mail(mail.outbox[0], 5 + 1) # global + personal
        #self._print_email_body(mail.outbox[0])
        
        mail.outbox = [] # Empty the test outbox
        call_command('senddigestmails', 'IMMEDIATELY')
        self.assertEquals(len(mail.outbox), 0)

