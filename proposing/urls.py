from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
import views
from models import Proposal

urlpatterns = patterns('',
    url(r'^$', views.index, name='proposals-index'),
    url(r'^(?P<proposal_slug>[-\w]+)/$', views.detail, name='proposals-detail'),
    url(r'^(?P<proposal_slug>[-\w]+)/(?P<post_id>\d+)/vote/(?P<updown>.+)/$', views.vote, name='posts-vote'),
    url(r'^(?P<proposal_slug>[-\w]+)/vote/(?P<updown>.+)/$', views.proposalvote, name='proposal-vote'),
    
    url(r'^proxy$', views.proxy, name='proxy-index'),
)
