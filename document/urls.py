'''
Created on Feb 4, 2013

@author: jonas
'''
from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
from models import FullDocument
from views import documentView

urlpatterns = patterns('document.views',
    url(r'^Doc(?P<pk>\d+)$', documentView,name='document-detail'),
)

