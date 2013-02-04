from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class OpinionUser(User):
    def hasValidatedEmail(self):
        return False
    
    def hasValidatedID(self):
        return False
    
    def isPayingMember(self):
        return False

class UserProfile(models.Model):  
    user = models.OneToOneField(OpinionUser, related_name="profile")

    @property
    def display_name(self):
        return self.user.username

### make sure profile is created when new user is created ###
def create_user_profile(sender, instance, created, **kwargs):
    if created:
       profile, created = UserProfile.objects.get_or_create(user=instance)  
post_save.connect(create_user_profile, sender=OpinionUser)