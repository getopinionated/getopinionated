from django.db import models
from django.contrib.auth.models import User, UserManager
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify

class CustomUser(User):
    slug = models.SlugField(unique=True)
    karma = models.IntegerField(default=0)
    
    # Use UserManager to get the create_user method, etc.
    objects = UserManager()

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
        return self.username
    
