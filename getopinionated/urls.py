#!/usr/bin/env python
# author: Jens Nyman (nymanjens.nj@gmail.com)

from django.conf.urls.defaults import *
from django.contrib import admin
import settings
import proposing.views
from getopinionated.settings import MEDIA_ROOT

admin.autodiscover()

urlpatterns = patterns('',
	(r'^admin/', include(admin.site.urls)),
	# (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^$', proposing.views.index, name="home-index"),
    (r'^accounts/', include('accounts.urls')),
	(r'^proposals/', include('proposing.urls')),
	(r'^document/', include('document.urls')),
	url(r'^tag/(?P<tag_slug>[-\w]+)/$', proposing.views.tagindex, name='tag-index'),
	(r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': MEDIA_ROOT, }),
	url(r'', include('social_auth.urls')),
)

