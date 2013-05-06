from social_auth.backends.facebook import FacebookBackend
from social_auth.backends.twitter import TwitterBackend
from social_auth.backends import google
from social_auth.signals import socialauth_registered
from urllib import urlopen
from getopinionated.settings import MEDIA_ROOT, MEDIA_URL
import os

def get_user_avatar(backend, details, response, social_user, uid,\
                    user, *args, **kwargs):
    url = None
    if backend.__class__ == FacebookBackend:
        url = "http://graph.facebook.com/%s/picture?type=large" % response['id']
 
    elif backend.__class__ == TwitterBackend:
        url = response.get('profile_image_url', '').replace('_normal', '')
 
    if url:
        avatar = urlopen(url).read()
        path = os.path.join(os.path.join(MEDIA_ROOT,'avatars'), user.slug + '.jpg')
        fout = open(path, "wb") #filepath is where to save the image
        fout.write(avatar)
        fout.close()
        user.avatar = MEDIA_URL + user.slug + '.jpg'
        user.save()