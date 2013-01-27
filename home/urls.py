#!/usr/bin/env python
# author: Jens Nyman (nymanjens.nj@gmail.com)

from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('home.views',
    url(r'^$', index),
)
