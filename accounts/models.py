from django.db import models
from django.contrib.auth.models import User, UserManager
from django.template.defaultfilters import slugify
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
    slug = models.SlugField(unique=True)
    karma = models.IntegerField(default=0)
    avatar = ImageField(upload_to='avatars/')
    member_since = models.DateTimeField(default=now())
    profile_views = models.IntegerField(default=0)
    
    REQUIRED_FIELDS = ['username']
    
    # Use UserManager to get the create_user method, etc.
    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)
        super(CustomUser, self).save(*args, **kwargs)

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
            if not image.content_type in ["png","jpg","jpeg","gif","bmp"]:
                raise forms.ValidationError(u'Only .png and .jpg images are allowed.')
            if w > 750 or h > 750:
                raise forms.ValidationError(u'That image is too big. The image needs to be 700x700px (or less).')
        return image
    
    def addView(self):
        self.profile_views += 1
        self.save()
    
    def canVote(self):
        if 'eID' in self.social_auth.all.values('provider'):
            return True
        return False
    