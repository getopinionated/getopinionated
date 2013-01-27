from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import proposal.urls

urlpatterns = patterns('',
    url(r'^proposal/', include(proposal.urls, namespace="proposal")),
    # Examples:
    # url(r'^$', 'getopinionated.views.home', name='home'),
    # url(r'^getopinionated/', include('getopinionated.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
