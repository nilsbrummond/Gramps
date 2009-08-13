from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
    (r'^view/(?P<view>(.*))/(?P<handle>(.*))$', 'grampsweb.views.dispatch'),
    (r'^view/(?P<view>(.*))/$', 'grampsweb.views.dispatch'),
    (r'^view/$', 'grampsweb.views.index'),
    (r'^$', 'grampsweb.homepage'),
)

