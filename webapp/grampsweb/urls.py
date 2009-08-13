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

urlpatterns += patterns('',
    # DANGEROUS in production:
     (r'^styles/(?P<path>.*)$', 'django.views.static.serve',
      {'document_root': 
          '/home/dblank/gramps/gep-013-server/webapp/html/styles', 
       'show_indexes': 
          True},
      ),
     (r'^images/(?P<path>.*)$', 'django.views.static.serve',
      {'document_root': 
          '/home/dblank/gramps/gep-013-server/webapp/html/images', 
       'show_indexes': 
          True},
      ),
)
