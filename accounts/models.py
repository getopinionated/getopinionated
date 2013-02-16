from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from common.stringify import niceBigInteger

class UserProfile(models.Model):  
    user = models.OneToOneField(User, related_name="profile")
    karma = models.IntegerField(default=0)
    
    @property
    def display_name(self):
        return self.user.username
    
### make sure profile is created when new user is created ###
def create_user_profile(sender, instance, created, **kwargs):
    if created:
       profile, created = UserProfile.objects.get_or_create(user=instance)  
post_save.connect(create_user_profile, sender=User)