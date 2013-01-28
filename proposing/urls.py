from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
import views
from models import Proposal

urlpatterns = patterns('',
    url(r'^$', views.index, name='proposals-index'),
    url(r'^specifics/(?P<pk>\d+)/$', DetailView.as_view(
            model=Proposal,
            template_name='proposal/detail.html'),
        name='proposals-detail'),
    url(r'^(?P<post_id>\d+)/vote/P<updown>.+/$', views.vote, name='proposals-vote'),
)
