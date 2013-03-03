from django.db import models
from django.contrib.auth.models import User, UserManager
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django import forms
from django.core.files.images import get_image_dimensions

class CustomUser(User):
    slug = models.SlugField(unique=True)
    karma = models.IntegerField(default=0)
    #avatar = models.ImageField(upload_to='/avatars/')
    
    # Use UserManager to get the create_user method, etc.
    objects = UserManager()

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
        avatar = self.cleaned_data['avatar']

        try:
            w, h = get_image_dimensions(avatar)

            #validate dimensions
            max_width = max_height = 100
            if w != max_width or h != max_height:
                raise forms.ValidationError(u'Please use an image that is %s x %s pixels.' % (max_width, max_height))

            #validate content type
            main, sub = avatar.content_type.split('/')
            if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
                raise forms.ValidationError(u'Please use a JPEG, GIF or PNG image.')

            #validate file size
            if len(avatar) > (20 * 1024):
                raise forms.ValidationError(u'Avatar file size may not exceed 20k.')

        except AttributeError:
            """
            Handles case when we are updating the user profile
            and do not supply a new avatar
            """
            pass

        return avatar
    
