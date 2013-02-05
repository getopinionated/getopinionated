from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
import views
from models import Proposal

urlpatterns = patterns('',
    url(r'^$', views.index, name='proposals-index'),
    url(r'^detail/(?P<proposal_id>\d+)/$', views.detail, name='proposals-detail'),
    url(r'^(?P<proposal_id>\d+)/(?P<post_id>\d+)/vote/(?P<updown>.+)/$', views.vote, name='posts-vote'),
)
