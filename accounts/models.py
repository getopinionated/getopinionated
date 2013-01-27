from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# note: get profile from user: user.get_profile()
class UserProfile(models.Model):  
    user = models.OneToOneField(User)

    def disiplay_name(self):
        return self.user.username

### make sure profile is created when new user is created ###
def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = UserProfile.objects.get_or_create(user=instance)  
post_save.connect(create_user_profile, sender=User)

