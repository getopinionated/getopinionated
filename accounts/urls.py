#!/usr/bin/env python

from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('accounts.views',
    url(r'^login/$', userlogin, name='user-login'),
    url(r'^register/$', userregister, name='user-register'),
    url(r'^update/$', profileupdate, name='profile-update'),
    url(r'^logout/$', userlogout, name='user-logout'),
    url(r'^user/(?P<username>.+)$', userprofile, name='user-profile'),
)

