from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
import views
from models import Proposal
from getopinionated.settings import STATIC_ROOT
from django.conf.global_settings import MEDIA_ROOT

urlpatterns = patterns('',
    url(r'^$', views.index, name='proposals-index'),
    url(r'^(?P<proposal_slug>[-\w]+)/$', views.detail, name='proposals-detail'),
    url(r'^(?P<proposal_slug>[-\w]+)/voters$', views.listofvoters, name='proposals-listofvoters'),
    url(r'^(?P<proposal_slug>[-\w]+)/(?P<post_id>\d+)/vote/(?P<updown>.+)/$', views.vote, name='posts-vote'),
    url(r'^(?P<proposal_slug>[-\w]+)/vote/(?P<score>.+)/$', views.proposalvote, name='proposal-vote'),
    
    url(r'^proxy$', views.proxy, name='proxy-index'),
)
