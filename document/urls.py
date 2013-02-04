'''
Created on Feb 4, 2013

@author: jonas
'''
from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
from models import FullDocument

urlpatterns = patterns('document.views',
    url(r'^Doc(?P<pk>\d+)$', DetailView.as_view(
            model=FullDocument,
            template_name='document/detail.html'),
        name='document-detail'),
)

