from django.db import models
from django.contrib.auth.models import User, UserManager
from django.template.defaultfilters import slugify
from libs.sorl.thumbnail import ImageField
from django import forms
from getopinionated.settings import MEDIA_ROOT

class CustomUser(User):
    slug = models.SlugField(unique=True)
    karma = models.IntegerField(default=0)
    avatar = ImageField(upload_to='avatars/')
    
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
        image = self.cleaned_data['avatar']
        if image:
            from django.core.files.images import get_image_dimensions
            w, h = get_image_dimensions(image)
            if not image.content_type in ["png","jpg","jpeg","gif","bmp"]:
                raise forms.ValidationError(u'Only .png and .jpg images are allowed.')
            if w > 750 or h > 750:
                raise forms.ValidationError(u'That image is too big. The image needs to be 700x700px (or less).')
        return image
    
from social_auth.backends.facebook import FacebookBackend
from social_auth.backends.twitter import TwitterBackend
from social_auth.backends import google
from social_auth.signals import socialauth_registered
def new_users_handler(sender, user, response, details, **kwargs):
    user.is_new = True
    if user.is_new:
        if "id" in response:
            
            from urllib2 import urlopen, HTTPError
            from django.template.defaultfilters import slugify
            from django.core.files.base import ContentFile
            
            try:
                url = None
                if sender == FacebookBackend:
                    url = "http://graph.facebook.com/%s/picture?type=large" \
                                % response["id"]
                elif sender == google.GoogleOAuth2Backend and "picture" in response:
                    url = response["picture"]
    
                elif sender == TwitterBackend:
                        url = response["profile_image_url"]
                        
                if url:
                    avatar = urlopen(url)
                    profile = CustomUser(user=user)
                    
                    profile.avatar.save(slugify(user.username + " social") + '.jpg', 
                            ContentFile(avatar.read()))              
                                    
                    profile.save()
    
            except HTTPError:
                pass
    
    return False
 
socialauth_registered.connect(new_users_handler, sender=None)