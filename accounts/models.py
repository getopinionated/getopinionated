from django.db import models
from django.contrib.auth.models import User, UserManager
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify

class CustomUser(User):
    slug = models.SlugField(unique=True)
    karma = models.IntegerField(default=0)
    
    # Use UserManager to get the create_user method, etc.
    objects = UserManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)
        super(CustomUser, self).save(*args, **kwargs)

    def isValidUserName(self, username):
        """ Check if slug derived from username already exists,
            the username is then automatically also unique.
            Keeps into account possibly  already existing object.
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
    
