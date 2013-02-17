from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify

class UserProfile(models.Model):  
    user = models.OneToOneField(User, related_name="profile")
    slug = models.SlugField(unique=True)
    karma = models.IntegerField(default=0)
    
    @staticmethod
    def isValidUserName(username):
        """ check if slug derived from username already exists,
            the username is then automatically also unique
        """
        userslug = slugify(username)
        try:
            UserProfile.objects.get(slug=userslug)
            return False
        except UserProfile.DoesNotExist:
            return True

    def isValidUserNameChange(self, username):
        """ same as isValidUserName, but keeps into account already
            existing model
        """
        userslug = slugify(username)
        try:
            profile = UserProfile.objects.get(slug=userslug)
            return self.id == profile.id
        except UserProfile.DoesNotExist:
            return True

    @property
    def display_name(self):
        return self.user.username
    
### make sure profile is created when new user is created ###
def create_user_profile(sender, instance, created, **kwargs):
    profile, created = UserProfile.objects.get_or_create(user=instance)
    if not created:
        profile.slug = slugify(instance.username)
        profile.save()
post_save.connect(create_user_profile, sender=User)