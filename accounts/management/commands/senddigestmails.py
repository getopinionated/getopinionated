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

class Command(LabelCommand):
    help = '''Send a mail to the users regarding new events.

              Arguments:
                  - label: possible values:
                        - "IMMEDIATELY": for users that chose to receive a mail immediately.
                        - "DAILY": for users that chose to receive a mail daily.
                        - "WEEKLY": for users that chose to receive a mail weekly.

    '''
    def handle_label(self, label, **options):
        # argument checks
        assert label in ['IMMEDIATELY', 'DAILY', 'WEEKLY']

        mail_cnt = 0
        for user in CustomUser.objects.filter(mail_frequency=label).all():

            # check if valid email
            if not user.email or '@' not in user.email:
                continue

            ### get all relevant events from queue ###
            events = []

            # pop personal events
            if user.mail_when_related_event:
                for item in PersonalEventEmailQueue.objects.filter(event_listener__user=user):
                    event_listener = item.event_listener
                    if not event_listener.seen_by_user:
                        events.append(event_listener.event.cast())
                    item.delete()
            
            # get global events
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
                        events.append(event)
                        item.already_mailed_users.add(user)

            events = list(OrderedDict.fromkeys(events)) # filter duplicate events while keeping order


            ################# BARRIER BETWEEN OLD AND NEW CODE #################
            # TODO:  fix template
            mail_text = "TODO"
    #         unsubscribecode = UnsubscribeCode(user=user, code=random.SystemRandom().getrandbits(64))
    #         unsubscribecode.save()
    #         mail_text = render_to_string('mails/digestmail.html', dictionary={
				# 'DOMAIN_NAME':settings.DOMAIN_NAME,
    #                             'new_proposals':new_proposals,
    #                             'voting_proposals':voting_proposals,
    #                             'finished_proposals':finished_proposals,
    #                             'unsubscribecode':unsubscribecode,
    #                             'label':label,
    #                             'user':user
    #                             })
            ################# BARRIER BETWEEN OLD AND NEW CODE #################

            ### send mail ###
            try:
                send_mail('GetOpinionated', mail_text, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                self.stdout.write("mail sent to {}".format(user.email))
                mail_cnt += 1

            except SMTPRecipientsRefused as e:
                self.stderr.write("mail refused to {}: {}".format(user.email, e))


        # wrap up
        self.stdout.write('Successfully sent the mails:\n')
        self.stdout.write('{} mails sent\n'.format(mail_cnt))

