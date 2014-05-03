from django.db import models
from django.contrib.auth.models import User, UserManager
from common.templatetags.filters import slugify
from libs.sorl.thumbnail import ImageField
from django import forms
from getopinionated.settings import MEDIA_ROOT
from django.utils.timezone import now

class CustomUserManager(UserManager):
    def create_user(self, username, *args, **kwargs):
        user = super(CustomUserManager, self).create_user(username, *args, **kwargs)
        user.slug = slugify(username)
        user.save()
        return user

class CustomUser(User):
    # constants
    MAIL_FREQUENCIES = [
        ('IMMEDIATELY', 'immediately'),
        ('DAILY', 'a daily digest'),
        ('WEEKLY', 'a weekly digest'),
        ('NEVER', 'never'),
    ]

    MAIL_WHEN_VOTING_STAGE_CHANGE = [
        ('ALWAYS', 'always'),
        ('I_REACTED', 'I reacted to the proposal (e.g.: endorsed, commented, starred, ...)'),
        ('I_STARRED', 'I starred the proposal'),
        ('NEVER', 'never'),
    ]

    # fields
    slug = models.SlugField(unique=True)
    karma = models.IntegerField(default=0)
    avatar = ImageField(upload_to='avatars/', null=True, blank=True)
    member_since = models.DateTimeField(default=now())
    profile_views = models.IntegerField(default=0)
    last_activity = models.DateTimeField(default=now())

    mail_frequency = models.CharField(max_length=20, choices=MAIL_FREQUENCIES, default='DAILY')
    mail_when_voting_stage_change = models.CharField(max_length=20, choices=MAIL_WHEN_VOTING_STAGE_CHANGE, default='ALWAYS')
    mail_when_related_event = models.BooleanField("Mail content: inform me when anything happens related to me (e.g.: "
            + "someone reacts to my proposal, added me as proxy or upvoted my comment)", default=True)


    # daily_digest = models.BooleanField("Get a daily digest in your mailbox",default=False)
    # weekly_digest = models.BooleanField("Get a weekly digest in your mailbox",default=True)
    # send_new = models.BooleanField("Get a mail for new proposals",default=True)
    # send_voting = models.BooleanField("Get a mail for proposals to vote",default=True)
    # send_finished = models.BooleanField("Get a mail for finished proposals",default=True)
    # send_favorites_and_voted = models.BooleanField("But only mail my favorites",default=False)


    REQUIRED_FIELDS = ['username']
    
    # Use UserManager to get the create_user method, etc.
    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)
        super(CustomUser, self).save(*args, **kwargs)

    @property
    def favorites(self):
        return self.favorites_including_disabled
        # return self.favorites_including_disabled.filter(enabled=True)

    def isValidUserName(self, username):
        """ Check if slug derived from username already exists,
            the username is then automatically also unique.
            Keeps into account possibility of already existing object.
        """
        userslug = slugify(username)
        try:
            profile = CustomUser.objects.get(slug=userslug)
            return self.id == profile.id
        except CustomUser.DoesNotExist:
            return True

    @property
    def display_name(self):
        return self.username
    
    def clean_avatar(self):
        image = self.cleaned_data['avatar']
        if image:
            from django.core.files.images import get_image_dimensions
            w, h = get_image_dimensions(image)
            if not image.content_type in ["png", "jpg", "jpeg", "gif", "bmp"]:
                raise forms.ValidationError(u'Only .png and .jpg images are allowed.')
            if w > 750 or h > 750:
                raise forms.ValidationError(u'That image is too big. The image needs to be 700x700px (or less).')
        return image
    
    def incrementViewCounter(self):
        self.profile_views += 1
        self.save()
    
    def canVote(self):
        if 'eID' in self.social_auth.all.values('provider'):
            return True
        return False

class UnsubscribeCode(models.Model):
    code = models.SlugField()
    user = models.ForeignKey(CustomUser)

class LoginCode(models.Model):
    code = models.TextField()
    user = models.ForeignKey(CustomUser)
    
