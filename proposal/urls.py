from django.conf.urls import patterns, url
from proposal import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^specifics/(?P<prop_id>\d+)/$', views.detail, name='detail'),
    url(r'^(?P<prop_id>\d+)/results/$', views.results, name='results'),
    url(r'^(?P<prop_id>\d+)/comment/$', views.comment, name='comment'),
    
)
