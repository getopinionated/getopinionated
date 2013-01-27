#!/usr/bin/env python
# author: Jens Nyman (nymanjens.nj@gmail.com)

from django.conf.urls.defaults import *
from django.contrib import admin
import settings
from home.views import index

admin.autodiscover()

urlpatterns = patterns('',
	(r'^admin/', include(admin.site.urls)),
	# (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^$', index, name="home-index"),
    (r'^accounts/', include('accounts.urls')),
	(r'^home/', include('home.urls')),
)

