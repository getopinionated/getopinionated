from social_auth.backends.facebook import FacebookBackend
from social_auth.backends.twitter import TwitterBackend
from social_auth.backends import google
from social_auth.signals import socialauth_registered
from urllib import urlopen
from getopinionated.settings import MEDIA_ROOT, MEDIA_URL
import os

#TODO: this is called on every login, this might be a little too much?
def get_user_avatar(backend, details, response, social_user, uid, \
                    user, *args, **kwargs):
    if user.avatar:
        return
    url = None
    if backend.__class__ == FacebookBackend:
        url = "http://graph.facebook.com/%s/picture?type=large" % response['id']
    elif backend.__class__ == google.GoogleOAuth2Backend and "picture" in response:
        url = response["picture"]
    elif backend.__class__ == TwitterBackend:
        url = response.get('profile_image_url', '').replace('_normal', '')
 
    if url:
        imagedata = urlopen(url).read()
        from PIL import Image as ImageObj
        from cStringIO import StringIO
        image = ImageObj.open(StringIO(imagedata))
        f = image.format.lower() 
        if not f in ["png", "jpg", "jpeg", "gif", "bmp"]:
            return # bad file format
        path = os.path.join(os.path.join(MEDIA_ROOT,'avatars'), user.slug + '.' + f)
        image.save(path)
        user.avatar = 'avatars/' + user.slug + '.' + f
        user.save()