import random
from collections import OrderedDict
from smtplib import SMTPRecipientsRefused

from django.core.management.base import BaseCommand, CommandError, NoArgsCommand, LabelCommand
from django.db.models import Q
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.timezone import datetime, timedelta, now
from django.conf import settings
from django.core.mail import send_mail

from accounts.models import CustomUser, UnsubscribeCode
from proposing.models import Proposal, ProxyProposalVote, Proxy, Tag
from event.models import PersonalEventEmailQueue, GlobalEventEmailQueue, ProposalLifeCycleEvent
from event.templatetags.event_filters import BundledEvent, listeners_to_bundled_events

class SendMailCommand(LabelCommand):
    help = '''Send a mail to the users regarding new events.

              Arguments:
                  - mail_frequency: possible values:
                        - "IMMEDIATELY": for users that chose to receive a mail immediately.
                        - "DAILY": for users that chose to receive a mail daily.
                        - "WEEKLY": for users that chose to receive a mail weekly.

    '''

    _HUMAN_READABLE_MAIL_FREQUENCY = {
        'IMMEDIATELY': '',
        'DAILY': 'daily ',
        'WEEKLY': 'weekly ',
    }

    def handle_label(self, mail_frequency, **options):
        # argument checks
        assert mail_frequency in ['IMMEDIATELY', 'DAILY', 'WEEKLY']

        mail_cnt = 0
        for user in CustomUser.objects.filter(mail_frequency=mail_frequency).all():

            # check if valid email
            if not user.email or '@' not in user.email:
                continue

            ### get all relevant events from queue ###
            # pop personal events
            personal_event_listeners = []
            if user.mail_when_related_event:
                for item in PersonalEventEmailQueue.objects.filter(event_listener__user=user):
                    event_listener = item.event_listener
                    if not event_listener.seen_by_user:
                        event_listener.event = event_listener.event.cast()
                        personal_event_listeners.append(event_listener)
                    item.delete()
            
            # get global events
            global_events = []
            for item in GlobalEventEmailQueue.objects.all():
                if user not in item.already_mailed_users.all():
                    event = item.event.cast()
                    eligible_event = False

                    if isinstance(event, ProposalLifeCycleEvent):
                        if user.mail_when_voting_stage_change == 'ALWAYS':
                            eligible_event = True
                        elif user.mail_when_voting_stage_change == 'I_REACTED':
                            eligible_event = user in event.get_listening_users()
                        elif user.mail_when_voting_stage_change == 'I_STARRED':
                            eligible_event = user in event.proposal.favorited_by.all()
                        elif user.mail_when_voting_stage_change == 'NEVER':
                            eligible_event = False

                    else:
                        raise NotImplementedError("Global events of type {} are not supported by the mailer yet.".format(type(event)))

                    if eligible_event:
                        global_events.append(event)
                        item.already_mailed_users.add(user)

            # filter duplicate events between personal events and global events
            personal_event_listeners = [p for p in personal_event_listeners if p.event in global_events]

            ### convert events to bundledevents ###
            bundledevents = []
            # add personal events
            bundledevents += listeners_to_bundled_events(personal_event_listeners)

            # add global events
            bundledevents += [BundledEvent(events=[event], unseen_events=[], reading_user=user) for event in global_events]

            ### get email text ###
            unsubscribecode = UnsubscribeCode(user=user, code=random.SystemRandom().getrandbits(64))
            unsubscribecode.save()
            mail_text = render_to_string('mails/digestmail.html', dictionary={
				'DOMAIN_NAME': settings.DOMAIN_NAME,
                'unsubscribecode': unsubscribecode,
                'mail_frequency': self._HUMAN_READABLE_MAIL_FREQUENCY[mail_frequency],
                'bundledevents': bundledevents,
                'user': user,
            })

            ### send mail ###
            try:
                send_mail('GetOpinionated', mail_text, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                self.stdout.write("mail sent to {}".format(user.email))
                mail_cnt += 1

            except SMTPRecipientsRefused as e:
                self.stderr.write("mail refused to {}: {}".format(user.email, e))


        # wrap up
        self.stdout.write('Successfully sent the mails:\n')
        self.stdout.write('{} mails sent\n'.format(mail_cnt))

