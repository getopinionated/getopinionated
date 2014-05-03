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
    url(r'^p/(?P<proposal_slug>[-\w]+)/voters/$', views.listofvoters, name='proposals-listofvoters'),
    url(r'^p/(?P<proposal_slug>[-\w]+)/edit/(?P<edit_comment_id>\d+)/$', views.detail, name='comment-edit'),
    url(r'^p/(?P<proposal_slug>[-\w]+)/reply/(?P<comment_id>\d+)/$', views.newcommentreply, name='new-commentreply'),
    url(r'^p/(?P<proposal_slug>[-\w]+)/editreply/(?P<edit_commentreply_id>\d+)/$', views.detail, name='commentreply-edit'),
    url(r'^positionproposal/new/$', views.positionproposalform, name='new-positionproposal'),
    url(r'^positionproposal/edit/(?P<edit_proposal_slug>[-\w]+)/$', views.positionproposalform, name='edit-positionproposal'),
    url(r'^proxy/$', views.show_proxies, name='proxy-index'),
    url(r'^proxy/(?P<tag_slug>[-\w]+)/$', views.show_proxies, name='proxy-index'),
    url(r'^ajax/favorite/(?P<proposal_slug>[-\w]+)/$', views.ajaxfavorite, name='ajax-favorite'),
    url(r'^ajax/endorse/(?P<proposal_slug>[-\w]+)/$', views.ajaxendorse, name='ajax-endorse'),
    url(r'^ajax/updownvote/(?P<post_id>[-\w]+)/(?P<updown>[-\w]+)/$', views.ajaxupdownvote, name='ajax-updownvote'),
    url(r'^ajax/vote/(?P<proposal_slug>[-\w]+)/(?P<score>.+)/$', views.ajaxproposalvote, name='ajax-proposal-vote'),
)
