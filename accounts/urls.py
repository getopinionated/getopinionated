#!/usr/bin/env python
import django.contrib.auth.views
from django.conf.urls import *
from views import userlogin, userregister, profileupdate, userlogout, userprofile, passwordreset
from accounts.views import userproposals, usercomments, uservotes, userproxies, \
    usertags, userproxyvotes, mailunsubscribe, logincode

urlpatterns = patterns('accounts.views',
    url(r'^login/$', userlogin, name='user-login'),
    url(r'^register/$', userregister, name='user-register'),
    url(r'^profile/$', profileupdate, name='profile-update'),
    url(r'^logout/$', userlogout, name='user-logout'),
    url(r'^user/(?P<userslug>[-\w]+)/$', userprofile, name='user-profile'),
    url(r'^user/(?P<userslug>[-\w]+)/proposals/$', userproposals, name='user-proposals'),
    url(r'^user/(?P<userslug>[-\w]+)/comments/$', usercomments, name='user-comments'),
    url(r'^user/(?P<userslug>[-\w]+)/votes/$', uservotes, name='user-votes'),
    url(r'^user/(?P<userslug>[-\w]+)/proxies/$', userproxies, name='user-proxies'),
    url(r'^user/(?P<userslug>[-\w]+)/tags/$', usertags, name='user-tags'),
    url(r'^user/(?P<userslug>[-\w]+)/proxy-votes/$', userproxyvotes, name='user-proxy-votes'),
    
    url(r'^unsubscribe/mail/(?P<code>[-\w]+)/$', mailunsubscribe , name='unsubscribe-mail'),
    url(r'^single-login/(?P<code>[-\w]+)/$', logincode , name='single-login-mail'),
    url(r'^passwordreset/$', passwordreset, name='password-reset'),
    url(r'^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', django.contrib.auth.views.password_reset_confirm, \
        {'post_reset_redirect' : '/accounts/password/done/', 'template_name': 'accounts/password-reset-confirm.html'}),
    url(r'^password/done/$', django.contrib.auth.views.password_reset_complete, \
        {'template_name': 'accounts/password-reset-complete.html'}),
)

