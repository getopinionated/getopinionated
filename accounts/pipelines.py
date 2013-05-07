from social_auth.backends.facebook import FacebookBackend
from social_auth.backends.twitter import TwitterBackend
from social_auth.backends import google
from social_auth.signals import socialauth_registered
from urllib import urlopen
from getopinionated.settings import MEDIA_ROOT, MEDIA_URL
import os

#TODO: this is called on every login, this might be a little too much?
def get_user_avatar(backend, details, response, social_user, uid,\
                    user, *args, **kwargs):
    url = None
    if backend.__class__ == FacebookBackend:
        url = "http://graph.facebook.com/%s/picture?type=large" % response['id']
    elif backend.__class__ == google.GoogleOAuth2Backend and "picture" in response:
        url = response["picture"]
    elif backend.__class__ == TwitterBackend:
        url = response.get('profile_image_url', '').replace('_normal', '')
 
    if url:
        avatar = urlopen(url).read()
        #from django.core.files.images import get_image_dimensions
        #w, h = get_image_dimensions(avatar)
        #if not avatar.content_type in ["png","jpg","jpeg","gif","bmp"]:
        #    return # bad file format
        path = os.path.join(os.path.join(MEDIA_ROOT,'avatars'), user.slug + '.jpg')
        fout = open(path, "wb") #filepath is where to save the image
        
        fout.write(avatar)
        fout.close()
        user.avatar = MEDIA_URL + 'avatars/' + user.slug + '.jpg'
        #user.avatar.width = w
        #user.avatar.height = h
        user.save()