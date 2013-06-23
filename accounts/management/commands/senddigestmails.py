from django.core.management.base import BaseCommand, CommandError, NoArgsCommand,\
    LabelCommand
from django.db.models import Q
from django.utils import timezone
from proposing.models import Proposal, ProxyProposalVote, Proxy, Tag
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from accounts.models import CustomUser, UnsubscribeCode
from django.utils import timezone
from django.utils.timezone import datetime, timedelta
import random
from django.core.mail import send_mail
from smtplib import SMTPRecipientsRefused

class Command(LabelCommand):
    help = '''Send a mail to the users regarding the updated proposals:
              Arguments:
                  daily when used for the daily digests
                  weekly when used for the weekly digests  '''
    
    def handle_label(self, label, **options):
        mail_cnt = 0
        
        for user in CustomUser.objects.all():
            
            mail_address = user.email
            if not mail_address:
                continue
            
            relevant_proposals = Proposal.objects.all()
            dt = None
            if user.daily_digest and label=='daily':
                dt = 1
            if user.weekly_digest and label=='weekly':
                dt = 7
            if dt is None:
                continue
            relevant_proposals = relevant_proposals.filter(voting_date__gte=datetime.now()-timedelta(days=dt),
                                                           voting_date__lte=datetime.now()) | \
                                 relevant_proposals.filter(expire_date__gte=datetime.now()-timedelta(days=dt),
                                                           expire_date__lte=datetime.now())
            
            if user.send_new:
                new_proposals = relevant_proposals.filter(voting_stage='DISCUSSION')
            else:
                new_proposals = None
                
            if user.send_voting:
                voting_proposals = relevant_proposals.filter(voting_stage='VOTING')
            else:
                voting_proposals = None
            
            if user.send_finished:
                finished_proposals = relevant_proposals.filter(voting_stage__in=['APPROVED','REJECTED'])
            else:
                finished_proposals = None
            
            if user.send_favorites_and_voted:
                new_proposals = None
                voting_proposals = voting_proposals.filter(favorited_by=user)
                finished_proposals = finished_proposals.filter(favorited_by=user) | finished_proposals.filter(proposal_votes__user=user) 
            
            if not new_proposals and not voting_proposals and not finished_proposals:
                continue #no need to send a mail if there's nothing in it
            
            unsubscribecode = UnsubscribeCode(user=user, code=random.SystemRandom().getrandbits(256))
            unsubscribecode.save()
            text = render_to_string('mails/digestmail.html', dictionary={
                                'new_proposals':new_proposals,
                                'voting_proposals':voting_proposals,
                                'finished_proposals':finished_proposals,
                                'unsubscribecode':unsubscribecode,
                                'label':label,
                                'user':user                                  
                                })
            
            print "mail sent to:",mail_address
            
            try:
                send_mail('GetOpinionated', text, 'opinion@pirateparty.be',[mail_address], fail_silently=False)
            except SMTPRecipientsRefused:
                print "refused"
                continue
            mail_cnt += 1
                
        self.stdout.write('Successfully sent the mails:\n')
        self.stdout.write('{} mails sent\n'.format(mail_cnt))
        