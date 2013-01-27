from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
from proposal import views
from proposal.models import Proposal

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(
            queryset=Proposal.objects.order_by('-create_date')[:5],
            context_object_name='latest_proposal_list',
            template_name='proposal/index.html'),
        name='index'),
    url(r'^specifics/(?P<pk>\d+)/$', DetailView.as_view(
            model=Proposal,
            template_name='proposal/detail.html'),
        name='detail'),
    url(r'^(?P<comment_id>\d+)/vote/$', views.vote, name='vote'),    
)
