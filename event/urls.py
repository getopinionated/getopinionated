from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^ajax/notificationbarclicked/$', views.ajax_notificationbarclicked, name='ajax-notificationbarclicked'),
)
