from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
import views
from models import Proposal
from getopinionated.settings import STATIC_ROOT
from django.conf.global_settings import MEDIA_ROOT

urlpatterns = patterns('',
    url(r'^$', views.proplist, name='proposals-index'),
    url(r'^list/(?P<list_type>[-\w]+)/$', views.proplist, name='proposals-list'),
    url(r'^p/(?P<proposal_slug>[-\w]+)/$', views.detail, name='proposals-detail'),
    url(r'^p/(?P<proposal_slug>[-\w]+)/voters$', views.listofvoters, name='proposals-listofvoters'),
    url(r'^p/(?P<proposal_slug>[-\w]+)/(?P<post_id>\d+)/vote/(?P<updown>.+)/$', views.vote, name='posts-vote'),
    url(r'^p/(?P<proposal_slug>[-\w]+)/vote/(?P<score>.+)/$', views.proposalvote, name='proposal-vote'),
    url(r'^p/(?P<proposal_slug>[-\w]+)/edit/(?P<comment_id>\d+)/$', views.editcomment, name='comment-edit'),
    url(r'^proxy/$', views.proxy, name='proxy-index'),
    url(r'^proxy/(?P<tag_slug>[-\w]+)$', views.proxy, name='proxy-index'),
    url(r'^ajax/favorite/(?P<proposal_slug>[-\w]+)$', views.ajaxfavorite, name='ajax-favorite'),
    url(r'^ajax/endorse/(?P<proposal_slug>[-\w]+)$', views.ajaxendorse, name='ajax-endorse'),
    url(r'^ajax/updownvote/(?P<post_id>[-\w]+)/(?P<updown>[-\w]+)$', views.ajaxupdownvote, name='ajax-updownvote'),
)
