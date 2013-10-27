'''
Created on Feb 4, 2013

@author: jonas
'''
from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
from models import FullDocument
from views import documentView

urlpatterns = patterns('document.views',
    url(r'^$', documentView, name='latest-default-document-detail'),
    url(r'^(?P<document_slug>[-\w]+)/$', documentView, name='latest-document-detail'),
    url(r'^(?P<document_slug>[-\w]+)/v(?P<document_version>\d+)/$', documentView, name='document-detail'),
)

